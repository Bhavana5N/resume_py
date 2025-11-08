"""
Unified job application generator using LangChain LLM modules.
Integrates job parser, resume generator, and cover letter generator.
"""
import os
import textwrap
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor

try:
    import openai_compat  # noqa: F401
except Exception:
    openai_compat = None

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from enhanced_prompts import ENHANCED_RESUME_PROMPT, ENHANCED_COVER_LETTER_PROMPT

load_dotenv()


class JobApplicationGenerator:
    """
    Unified class that generates tailored resume and cover letter from job description.
    Simplifies the original multi-file structure for our use case.
    """
    
    def __init__(self, openai_api_key: str = None):
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required")
        
        model_name = os.getenv("OPENAI_RESUME_MODEL", "gpt-4o")
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            temperature=0.4,
        )
        self.resume_text = None

    @staticmethod
    def _normalize_meta_field(value: str | None) -> str:
        if not value:
            return ""
        cleaned = value.strip()
        if cleaned.lower() in {"not specified", "not specified."}:
            return ""
        return cleaned

    @staticmethod
    def _preprocess_template(template: str) -> str:
        """Remove leading whitespace and indentation."""
        return textwrap.dedent(template)

    def set_resume(self, resume_text: str) -> None:
        """Set the resume text to be used for generation."""
        self.resume_text = resume_text

    @staticmethod
    def _compose_job_context(job_description: str, job_summary: str | None) -> str:
        """Combine summary and description while keeping size manageable."""
        description = (job_description or "").strip()
        summary = (job_summary or "").strip() if job_summary else ""

        context_parts = []
        if summary:
            context_parts.append("Job Summary:")
            context_parts.append(summary)
        if description:
            if summary:
                context_parts.append("\nFull Job Description:")
            context_parts.append(description)

        context = "\n".join(context_parts).strip() or "No job description provided."
        max_chars = 8000
        if len(context) > max_chars:
            context = context[:max_chars] + "\n\n[Content truncated for brevity]"
        return context

    def summarize_job_description(self, job_description: str) -> str:
        """
        Summarize job description to extract key requirements.
        Based on llm_job_parser functionality.
        """
        template = self._preprocess_template("""
        You are an expert at analyzing job descriptions.
        Extract and summarize the key information from this job description:
        
        - Role/Title
        - Key Responsibilities (top 5)
        - Required Skills and Qualifications
        - Preferred/Nice-to-have Skills
        - Company Culture/Values (if mentioned)
        
        Job Description:
        {text}
        
        Provide a concise, structured summary.
        """)
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"text": job_description})

    def generate_tailored_resume(
        self,
        job_description: str,
        company: str,
        role: str,
        job_summary: str | None = None,
    ) -> str:
        """
        Generate ATS-optimized resume tailored to job description.
        Based on llm_generate_resume_from_job functionality.
        """
        if not self.resume_text:
            raise ValueError("Base resume text must be set before generating outputs.")

        company = self._normalize_meta_field(company)
        role = self._normalize_meta_field(role)

        summary = job_summary or self.summarize_job_description(job_description)
        job_context = self._compose_job_context(job_description, summary)

        template = self._preprocess_template(ENHANCED_RESUME_PROMPT)

        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        
        return chain.invoke({
            "company_name": company,
            "job_title": role,
            "job_description": job_context,
            "resume_text": self.resume_text,
        })

    def generate_cover_letter(
        self,
        job_description: str,
        company: str,
        role: str,
        job_summary: str | None = None,
    ) -> str:
        """
        Generate compelling cover letter based on job description and resume.
        Based on llm_generate_cover_letter_from_job functionality.
        """
        if not self.resume_text:
            raise ValueError("Base resume text must be set before generating outputs.")

        company = self._normalize_meta_field(company)
        role = self._normalize_meta_field(role)

        summary = job_summary or self.summarize_job_description(job_description)
        job_context = self._compose_job_context(job_description, summary)

        template = self._preprocess_template(ENHANCED_COVER_LETTER_PROMPT)

        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        
        return chain.invoke({
            "company_name": company,
            "job_title": role,
            "job_description": job_context,
            "resume_text": self.resume_text,
        })

    def generate_application_package(
        self,
        job_description: str,
        company: str,
        role: str,
        parallel: bool = True
    ) -> Dict[str, str]:
        """
        Generate both tailored resume and cover letter.
        
        Args:
            job_description: Full job description text
            company: Company name
            role: Role/title
            parallel: Generate resume and cover letter in parallel (faster)
        
        Returns:
            dict: {"resume": str, "cover_letter": str, "job_summary": str}
        """
        # Always generate job summary first
        job_summary = self.summarize_job_description(job_description)

        company_clean = self._normalize_meta_field(company)
        role_clean = self._normalize_meta_field(role)
        
        if parallel:
            # Generate resume and cover letter in parallel
            with ThreadPoolExecutor(max_workers=2) as executor:
                resume_future = executor.submit(
                    self.generate_tailored_resume,
                    job_description,
                    company_clean,
                    role_clean,
                    job_summary,
                )
                cover_letter_future = executor.submit(
                    self.generate_cover_letter,
                    job_description,
                    company_clean,
                    role_clean,
                    job_summary,
                )
                
                return {
                    "resume": resume_future.result(),
                    "cover_letter": cover_letter_future.result(),
                    "job_summary": job_summary
                }
        else:
            # Sequential generation
            return {
                "resume": self.generate_tailored_resume(
                    job_description, company_clean, role_clean, job_summary
                ),
                "cover_letter": self.generate_cover_letter(
                    job_description, company_clean, role_clean, job_summary
                ),
                "job_summary": job_summary
            }


"""
Enhanced Resume Generation Prompts
Focuses on 2-page format, 10 bullet professional summary, and most recent relevant experience
"""

ENHANCED_RESUME_PROMPT = """
You are an expert resume writer creating a tailored, ATS-optimized resume for a specific job application.

**Job Details:**
Company: {company_name}
Position: {job_title}
Job Description: {job_description}

**Candidate's Background:**
{resume_text}

**CRITICAL REQUIREMENTS:**

1. **Header Section:**
   - Candidate's full name
   - Contact: Email | Phone | GitHub | LinkedIn (all on one line)

2. **PROFESSIONAL SUMMARY - MUST HAVE EXACTLY 10 BULLET POINTS:**
   Section header: "PROFESSIONAL SUMMARY"
   - Bullet 1: Years of experience + core expertise relevant to this role
   - Bullet 2: Specific quantifiable achievement (#1 - must include numbers/percentages)
   - Bullet 3: Specific quantifiable achievement (#2 - must include numbers/percentages)
   - Bullet 4: Technical skills/technologies from job description
   - Bullet 5: Leadership/team collaboration achievement
   - Bullet 6: System architecture or scalability achievement
   - Bullet 7: Process improvement or efficiency gain
   - Bullet 8: Cross-functional collaboration or stakeholder management
   - Bullet 9: Domain expertise or industry-specific knowledge
   - Bullet 10: Professional development, certifications, or thought leadership
   
   **Each bullet MUST:**
   - Start with a strong action verb (Led, Architected, Developed, Optimized, Implemented)
   - Include specific numbers, percentages, or measurable impact
   - Be 1-2 lines maximum
   - Directly relate to the job requirements

3. **WORK EXPERIENCE Section:**
   Section header: "WORK EXPERIENCE"
   
   For EACH position, use this EXACT format:
   ```
   Job Title | Actual Company Name
   Month Year – Month Year | City, State/Country
   • Achievement with quantifiable result (e.g., "Reduced costs by 40% ($500K annually)")
   • Achievement with quantifiable result
   • Achievement with quantifiable result
   • Achievement with quantifiable result
   ```
   
   **CRITICAL:** 
   - Use the REAL company names from the candidate's background
   - Use the REAL job titles from the candidate's background
   - Include 2-3 most recent positions
   - Each position must have 4-6 bullet points
   - Focus on achievements that match the target job requirements

4. **EDUCATION Section:**
   Section header: "EDUCATION"
   ```
   Degree Name | University Name
   Month Year – Month Year | GPA: X.X/4.0
   - Thesis/Notable achievement (if applicable)
   ```

5. **TECHNICAL SKILLS Section:**
   Section header: "TECHNICAL SKILLS"
   Organize in categories with clear labels (use ** for bold category names):
   ```
   **Programming Languages:** Python, C++, JavaScript, Java, Shell Scripting
   **Frameworks & Platforms:** Django, Flask, React JS, PyTorch, TensorFlow, Keras, OpenCV
   **Cloud Technologies:** AWS (S3, Lambda, CloudFormation, DynamoDB, SageMaker), Azure
   **Automation & DevOps Tools:** Docker, Jenkins, CI/CD Pipelines, Terraform, Ansible
   **Data Management:** Snowflake, PostgreSQL, SQLite, SQL, DynamoDB
   **Visualization Tools:** Plotly, Dash, Matplotlib
   **Version Control:** Git, GitHub, Bitbucket
   **Operating Systems:** Linux (Ubuntu, RedHat), macOS
   ```
   - Prioritize skills from the job description
   - Keep it concise and organized
   - Use bold (**text**) for category names

6. **FUNCTIONAL EXPERTISE Section:**
   Section header: "FUNCTIONAL EXPERTISE"
   Format like Technical Skills with categories:
   ```
   **Machine Learning & AI:** ML pipeline development, clustering algorithms, trust modeling, Bayesian models
   **Software Integration & Validation:** Middleware analysis, system debugging, testbench validation
   **Pipeline Automation:** CI/CD pipeline creation, PR automation, dependency management
   **Full Stack Development:** Flask, Django, Dash, React JS, SQL databases
   **Computer Vision:** Camera object detection, 2D to 3D box mapping, emergency braking systems
   ```

7. **KEY ACHIEVEMENTS Section:**
   Section header: "KEY ACHIEVEMENTS"
   Format with bullet points (extract from work experience):
   ```
   • Reduced manual validation and testing efforts by 70% through automation using Jenkins, Docker, and Azure
   • Improved workflow efficiency by automating PR creation and dependency management with Azure Pipelines
   • Created AUTOSIM prototype supporting multiple integrations, reducing manual effort by 70%
   • Migrated object detection from 2D to 3D box mapping, improving system accuracy
   • Enhanced deployment reliability by automating installation processes across virtual and real nodes
   • Designed innovative tools that reduced release times and improved deployment workflows by 60%
   ```
   - Extract 5-8 most impressive achievements from work experience
   - Each achievement must have quantifiable impact (%, time saved, cost reduction)
   - Focus on achievements relevant to the target job

8. **PUBLICATIONS Section:**
   Section header: "PUBLICATIONS"
   Format with bullet points:
   ```
   • Bhavana Nare, et al., "Computational Trust Framework for Human-Robot Teams," IEEE Xplore, Document 11127674, 2024. Available at https://ieeexplore.ieee.org/document/11127674
   ```
   - Include all publications with full citations
   - Add URLs if available

9. **Optional Sections (if relevant):**
   - CERTIFICATIONS (if applicable)
   - KEY PROJECTS (if highly relevant)

**OUTPUT FORMAT:**
```
Full Name
email@domain.com | Phone | github.com/username | linkedin.com/in/username

PROFESSIONAL SUMMARY
• [Bullet point 1 with numbers]
• [Bullet point 2 with numbers]
• [Bullet point 3 with numbers]
• [Bullet point 4 with numbers]
• [Bullet point 5 with numbers]
• [Bullet point 6 with numbers]
• [Bullet point 7 with numbers]
• [Bullet point 8 with numbers]
• [Bullet point 9 with numbers]
• [Bullet point 10 with numbers]

WORK EXPERIENCE

Job Title | Company Name
Month Year – Month Year | Location
• Achievement 1 with quantifiable results
• Achievement 2 with quantifiable results
• Achievement 3 with quantifiable results
• Achievement 4 with quantifiable results

[Repeat for 2-3 positions]

EDUCATION

Degree | University
Month Year – Month Year | GPA: X.X/4.0

TECHNICAL SKILLS

**Programming Languages:** Python, C++, JavaScript, Java
**Frameworks & Platforms:** Django, Flask, React JS, PyTorch, TensorFlow
**Cloud Technologies:** AWS (S3, Lambda, CloudFormation), Azure
**Automation & DevOps Tools:** Docker, Jenkins, CI/CD, Terraform
**Data Management:** PostgreSQL, SQLite, SQL, DynamoDB
**Visualization Tools:** Plotly, Dash, Matplotlib
**Version Control:** Git, GitHub, Bitbucket

FUNCTIONAL EXPERTISE

**Machine Learning & AI:** ML pipeline development, clustering, trust modeling
**Software Integration & Validation:** Middleware analysis, debugging, testbench validation
**Pipeline Automation:** CI/CD pipeline creation, PR automation, dependency management
**Full Stack Development:** Flask, Django, Dash, React JS, SQL databases
**Computer Vision:** Camera object detection, 2D to 3D mapping, emergency braking systems

KEY ACHIEVEMENTS

• Reduced manual validation and testing efforts by 70% through automation using Jenkins, Docker, and Azure
• Improved workflow efficiency by automating PR creation and dependency management with Azure Pipelines
• Created AUTOSIM prototype supporting multiple integrations, reducing manual effort by 70%
• Migrated object detection from 2D to 3D box mapping, improving system accuracy
• Enhanced deployment reliability by automating installation processes across virtual and real nodes
• Designed innovative tools that reduced release times and improved deployment workflows by 60%

PUBLICATIONS

• Bhavana Nare, et al., "Computational Trust Framework for Human-Robot Teams," IEEE Xplore, Document 11127674, 2024. Available at https://ieeexplore.ieee.org/document/11127674
```

**CRITICAL RULES:**
- NO generic placeholders like "Company" or "Position"
- USE REAL NAMES from the candidate's background
- EXACTLY 10 bullet points in Professional Summary
- EVERY achievement must include numbers/metrics
- Focus on relevance to the target job
"""

ENHANCED_COVER_LETTER_PROMPT = """
You are an expert cover letter writer creating a compelling, personalized cover letter for a specific job application.

**Job Details:**
Company: {company_name}
Position: {job_title}
Job Description: {job_description}

**Candidate's Background:**
{resume_text}

**Requirements:**
1. Create a 1-PAGE cover letter that:
   - Opens with a compelling hook that shows genuine interest in the company and role
   - Demonstrates understanding of the company's mission, products, or recent news
   - Highlights 3-4 most relevant achievements that directly address the job requirements
   - Provides specific examples with quantifiable results
   - Shows cultural fit and alignment with company values
   - Closes with a confident call to action

2. Structure:
   - Opening paragraph: Hook + Why this company + Why this role
   - Body paragraphs (2-3): Relevant achievements and skills
   - Closing paragraph: Value proposition + Next steps

3. Tone:
   - Professional yet personable
   - Confident without being arrogant
   - Enthusiastic about the opportunity
   - Match the company's communication style (formal for enterprise, casual for startups)

4. Content Guidelines:
   - Don't repeat the resume - provide context and stories
   - Use the STAR method (Situation, Task, Action, Result) for examples
   - Connect your experience directly to their needs
   - Show, don't tell (use specific examples, not generic claims)
   - Keep it concise - aim for 3-4 paragraphs total

**Output Format:**
Provide the complete cover letter as formatted text, ready to be converted to PDF.
Do NOT include the date, address, or "To Whom It May Concern" - these will be added automatically.
Start with "Dear Hiring Manager," or "Dear [Company] Team,"
End with "Sincerely," (closing signature will be added automatically).
"""

PROFESSIONAL_SUMMARY_PROMPT = """
Generate a compelling professional summary with EXACTLY 10 bullet points for a {job_title} position at {company_name}.

**Job Description:**
{job_description}

**Candidate Background:**
{resume_text}

**Instructions:**
Create 10 impactful bullet points that:
1. Highlight the most relevant skills and experience for THIS specific role
2. Include quantifiable achievements (%, $, scale, impact)
3. Mention key technologies/skills from the job description
4. Show progression and leadership
5. Demonstrate domain expertise
6. Are action-oriented and results-focused
7. Are concise (1-2 lines each)
8. Use strong verbs (Led, Architected, Scaled, Optimized, etc.)
9. Show both technical depth and business impact
10. Create a compelling narrative of the candidate's value

**Format:**
Return ONLY the 10 bullet points, one per line, starting with "•"
Do NOT include a header or section title.
Do NOT include any other text.

Example format:
• Led cross-functional team of 12 engineers to deliver cloud migration, reducing infrastructure costs by 40% ($2M annually)
• Architected and implemented microservices platform serving 50M+ daily active users with 99.99% uptime
...
"""

WORK_EXPERIENCE_PROMPT = """
Generate a tailored work experience section focusing on the MOST RECENT and MOST RELEVANT positions for a {job_title} role at {company_name}.

**Job Description:**
{job_description}

**Candidate's Work History:**
{experience_text}

**Instructions:**
1. Select the 2-3 most recent and relevant positions
2. For each position, provide:
   - Position Title | Company Name
   - Employment Period | Location
   - 4-6 impactful bullet points that:
     * Align with the job requirements
     * Include quantifiable results
     * Highlight relevant technologies and skills
     * Show increasing responsibility and impact
     * Use strong action verbs

3. If the candidate has older but highly relevant experience, include 1 additional position with 3-4 bullets

**Prioritization Criteria:**
- Relevance to target role: 50%
- Recency: 30%
- Impact and achievements: 20%

**Format:**
Position Title | Company Name
Month Year - Month Year | Location
• Achievement/responsibility with quantifiable impact
• Achievement/responsibility with quantifiable impact
...

[Repeat for each position]
"""


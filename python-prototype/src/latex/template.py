"""
LaTeX Templates for Alex Rivera's Resume and Cover Letter.
Contains verbatim macro structures from Alex's working resume template.
"""

RESUME_LATEX_TEMPLATE = r"""
\documentclass[letterpaper,11pt]{article}
\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\input{glyphtounicode}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.7in}
\addtolength{\textheight}{1.3in}
\urlstyle{same}
\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{\vspace{-4pt}\scshape\raggedright\large}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]
\pdfgentounicode=1

\newcommand{\resumeItem}[1]{\item\small{#1 \vspace{-2pt}}}
\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}
\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}
\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}
\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}
\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label=\textbullet]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}

%----------HEADING----------
\begin{center}
    \textbf{\Large \scshape {{ candidate_name }}} \\ \vspace{1pt}
    \small {{ phone }} $|$ \href{mailto:{{ email }}}{\underline{{{ email }}}} $|$
    \href{https://{{ linkedin }}}{\underline{{{ linkedin }}}} $|$
    \href{https://{{ github }}}{\underline{{{ github }}}} $|$
    \href{https://{{ leetcode }}}{\underline{{{ leetcode }}}}
\end{center}

%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    \resumeSubheading
      { {{ education_institution }} }{ {{ education_location }} }
      { {{ education_degree }} }{ {{ education_years }} }
  \resumeSubHeadingListEnd

%-----------PROGRAMMING SKILLS-----------
\section{Technical Skills}
 \begin{itemize}[leftmargin=0.15in, label=\textbullet]
    \small{\item{
     \textbf{Core Stack}: {{ skills_line_1 }} \\
     \textbf{Databases \& Infrastructure}: {{ skills_line_2 }} \\
     \textbf{Tools \& Frameworks}: {{ skills_line_3 }}
    }}
 \end{itemize}

%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart
    {% for exp in experience_items %}
    \resumeSubheading
      { {{ exp.company }} }{ {{ exp.period }} }
      { {{ exp.role }} }{ {{ exp.location }} }
      \resumeItemListStart
        {% for bullet in exp.bullets %}
        \resumeItem{ {{ bullet }} }
        {% endfor %}
      \resumeItemListEnd
    {% endfor %}
  \resumeSubHeadingListEnd

%-----------PROJECTS-----------
\section{Projects}
    \resumeSubHeadingListStart
      {% for proj in project_items %}
      \resumeProjectHeading
          { \textbf{ {{ proj.name }} } $|$ \emph{ {{ proj.tech_stack }} } }{ {{ proj.period }} }
          \resumeItemListStart
            {% for bullet in proj.bullets %}
            \resumeItem{ {{ bullet }} }
            {% endfor %}
          \resumeItemListEnd
      {% endfor %}
    \resumeSubHeadingListEnd

%-----------ACHIEVEMENTS-----------
\section{Achievements \& Contributions}
 \begin{itemize}[leftmargin=0.15in, label=\textbullet]
    {% for ach in achievement_items %}
    \item\small{\textbf{ {{ ach.title }} }: {{ ach.text }}}
    {% endfor %}
 \end{itemize}

\end{document}
"""

COVER_LETTER_LATEX_TEMPLATE = r"""
\documentclass[letterpaper,11pt]{article}
\usepackage[empty]{fullpage}
\usepackage[hidelinks]{hyperref}
\usepackage[english]{babel}

\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.7in}
\addtolength{\textheight}{1.3in}
\raggedbottom
\raggedright

\begin{document}

\begin{center}
    \textbf{\Large \scshape {{ candidate_name }}} \\ \vspace{1pt}
    \small {{ phone }} $|$ \href{mailto:{{ email }}}{\underline{{{ email }}}} $|$
    \href{https://{{ linkedin }}}{\underline{{{ linkedin }}}} $|$
    \href{https://{{ github }}}{\underline{{{ github }}}}
\end{center}

\vspace{10pt}

\today

\vspace{10pt}

\textbf{To the Hiring Team at {{ company_name }}},

\vspace{10pt}

{{ paragraph_1 }}

\vspace{10pt}

{{ paragraph_2 }}

\vspace{10pt}

{{ paragraph_3 }}

\vspace{15pt}

Sincerely, \\
\textbf{{{ candidate_name }}}

\end{document}
"""

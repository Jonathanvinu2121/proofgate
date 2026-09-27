"""
Seed Ground Truth Dataset for Alex Rivera.
Contains exact candidate metadata, atomic experience bullets, projects, achievements,
confirmed tool proficiencies, and explicit known skill gaps.
Do NOT invent or extrapolate additional experience.
"""

CANDIDATE_INFO = {
    "name": "Alex Rivera",
    "degree": "B.Tech CSE",
    "institution": "State Technical University",
    "graduation_years": "2022–2026",
    "graduation_status": "pending conferral",
    "total_experience": "~1.5 years combined contract/founder engineering experience",
    "location": "India",
    "email": "alex.rivera@example.com",
    "phone": "+91 98765 43210",
    "github": "github.com/alexrivera-dev",
    "linkedin": "linkedin.com/in/alexrivera",
    "leetcode": "leetcode.com/u/alexrivera-dev",
    "core_stack": [
        "Node.js", "Express.js", "Python", "FastAPI", "PostgreSQL",
        "MongoDB", "Redis", "Docker", "React", "Java", "Spring Boot"
    ]
}

GROUND_TRUTH_DATA = {
    "experience": [
        {
            "id": "EXP-1",
            "role": "Backend Developer (Contract)",
            "company": "Northwind Labs",
            "period": "Oct 2025–May 2026",
            "location": "Remote",
            "text": "Delivered RESTful APIs and end-to-end integrations connecting React frontends with high-throughput backend services for 4+ client projects, owning each pipeline from design through deployment.",
            "category": "technical",
            "technologies": ["Node.js", "Express.js", "React", "REST API", "Backend Integration"]
        },
        {
            "id": "EXP-2",
            "role": "Backend Developer (Contract)",
            "company": "Northwind Labs",
            "period": "Oct 2025–May 2026",
            "location": "Remote",
            "text": "Optimized slow PostgreSQL queries from ~600ms to under 100ms through targeted indexing and schema restructuring; built a reusable error-handling and logging layer adopted across all client projects.",
            "category": "technical",
            "technologies": ["PostgreSQL", "Database Optimization", "Indexing", "Logging", "Error Handling"]
        },
        {
            "id": "EXP-3",
            "role": "Backend Developer (Contract)",
            "company": "Northwind Labs",
            "period": "Oct 2025–May 2026",
            "location": "Remote",
            "text": "Personally designed, built, and deployed a real-time kitchen order and POS system for a live restaurant client, processing 100+ orders daily in production with zero reported downtime.",
            "category": "technical",
            "technologies": ["Node.js", "PostgreSQL", "POS System", "Production", "Real-Time System"],
            "note": "LIVE production system built through agency/founder work — NOT open source"
        },
        {
            "id": "EXP-4",
            "role": "Software Developer (Contract)",
            "company": "Brightpath Digital",
            "period": "Mar 2025–Sep 2025",
            "location": "Remote",
            "text": "Shipped full-stack features across React and Node.js with real-time WebSocket support across 3+ internal products, maintaining stable performance under 50+ concurrent connections with zero downtime.",
            "category": "technical",
            "technologies": ["React", "Node.js", "WebSockets", "Full-Stack", "Real-Time"]
        }
    ],
    "projects": [
        {
            "id": "PROJ-1",
            "name": "KOT/POS System (Rebuild)",
            "technologies": ["Node.js", "PostgreSQL", "MongoDB", "Docker", "WebSockets"],
            "period": "2026",
            "summary": "An independent rebuild of the live production system's core architecture, built afterward as a shareable portfolio piece — NOT the same codebase as the live system. Dual-database architecture: PostgreSQL for ACID-compliant transactional state, MongoDB for scalable document storage, real-time WebSocket sync at <50ms latency. Debugged a concurrency race condition (two terminals updating the same order simultaneously) by replacing wall-clock ordering with logical Lamport-style timestamps to establish causal order.",
            "bullets": [
                "Architected a dual-database pattern using PostgreSQL for transactional consistency and MongoDB for flexible document storage, maintaining <50ms WebSocket sync.",
                "Resolved multi-terminal race conditions during peak load by implementing Lamport logical timestamps to establish deterministic causal ordering across asynchronous events."
            ],
            "category": "technical",
            "is_portfolio_rebuild": True
        },
        {
            "id": "PROJ-2",
            "name": "API Gateway & Distributed Rate Limiting",
            "technologies": ["Node.js", "Express.js", "Redis", "MongoDB", "JWT"],
            "period": "2025",
            "summary": "Centralized API gateway featuring JWT authentication, dynamic routing, and rate limiting (token bucket + sliding window algorithms) backed by Redis, with MongoDB for persistence. Implemented circuit breaker patterns and multi-tenant traffic isolation supporting 10+ concurrent tenants under load testing with zero cross-tenant bleed.",
            "bullets": [
                "Engineered a distributed rate limiter supporting token bucket and sliding window algorithms backed by Redis, achieving multi-tenant traffic isolation for 10+ tenants.",
                "Implemented circuit breaker resiliency patterns and JWT dynamic authentication routing to prevent systemic service degradation under peak load testing."
            ],
            "category": "technical"
        },
        {
            "id": "PROJ-3",
            "name": "Smart Health Surveillance System",
            "technologies": ["Python", "FastAPI", "React", "Node.js", "MongoDB Atlas", "XGBoost"],
            "period": "2025",
            "summary": "Waterborne disease outbreak detection platform utilizing XGBoost anomaly detection (achieving 87% precision). Powered by production Python/FastAPI microservices and asynchronous inference workflows. Integrated multi-channel alerts (Twilio SMS / Nodemailer email) across 3 role-based dashboards (Community User, ASHA Worker, Admin) alongside an automated ML retraining feedback loop.",
            "bullets": [
                "Built asynchronous FastAPI ML inference microservices utilizing XGBoost anomaly detection to identify waterborne disease outbreaks with 87% precision.",
                "Designed multi-role automated alerting pipelines across 3 user tiers (Community, ASHA Worker, Admin) with automated ML model retraining feedback loops."
            ],
            "category": "technical"
        }
    ],
    "achievements": [
        {
            "id": "ACH-1",
            "title": "National Innovation Hackathon Finalist",
            "text": "Selected as a national finalist (top 3% among 44,000+ competing teams across India) in 2023.",
            "category": "achievement",
            "technologies": ["System Design", "Problem Solving", "Hackathon"]
        },
        {
            "id": "ACH-2",
            "title": "University Hackathon - 1st Place",
            "text": "Awarded 1st place in the STU internal campus-wide hackathon (2024).",
            "category": "achievement",
            "technologies": ["Rapid Prototyping", "Full-Stack Development"]
        },
        {
            "id": "ACH-3",
            "title": "LeetCode Competitive Programming",
            "text": "Consistent Data Structures and Algorithms practice on LeetCode (profile: leetcode.com/u/alexrivera-dev).",
            "category": "achievement",
            "technologies": ["Java", "DSA", "Algorithm Optimization"]
        },
        {
            "id": "ACH-4",
            "title": "Open Source & Automation",
            "text": "Contributed to public-apis repository and engineered a custom job-search automation system (2025).",
            "category": "achievement",
            "technologies": ["Git", "GitHub", "Python", "Automation"]
        }
    ],
    "confirmed_tools": [
        "Jira", "Notion", "Google Colab", "Docker", "Git", "GitHub", "Postman", "Selenium"
    ],
    "explicit_known_gaps": [
        {"id": "GAP-AWS", "name": "AWS", "description": "Amazon Web Services cloud platform experience"},
        {"id": "GAP-GCP", "name": "GCP", "description": "Google Cloud Platform experience"},
        {"id": "GAP-AZURE", "name": "Azure", "description": "Microsoft Azure cloud platform experience"},
        {"id": "GAP-TS", "name": "TypeScript", "description": "TypeScript static typing language"},
        {"id": "GAP-NEXT", "name": "Next.js", "description": "Next.js React web framework"},
        {"id": "GAP-PRISMA", "name": "Prisma ORM", "description": "Prisma ORM database toolkit"},
        {"id": "GAP-GRAPHQL", "name": "GraphQL", "description": "GraphQL query language and API runtime"},
        {"id": "GAP-K8S", "name": "Kubernetes", "description": "Kubernetes container orchestration platform"},
        {"id": "GAP-GOLANG", "name": "Golang", "description": "Go programming language"},
        {"id": "GAP-ELIXIR", "name": "Elixir", "description": "Elixir concurrent functional programming language"},
        {"id": "GAP-HASKELL", "name": "Haskell", "description": "Haskell purely functional programming language"},
        {"id": "GAP-TESTING", "name": "Jest/Mocha/PyTest", "description": "Formal unit testing frameworks (Jest, Mocha, PyTest)"},
        {"id": "GAP-CICD", "name": "CI/CD", "description": "Continuous Integration and Continuous Deployment pipeline setup"},
        {"id": "GAP-STRIPE", "name": "Stripe", "description": "Stripe payment gateway integration"},
        {"id": "GAP-OBSERVABILITY", "name": "Observability", "description": "Observability tooling (Prometheus, Grafana, OpenTelemetry)"}
    ]
}

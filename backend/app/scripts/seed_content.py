"""Seed realistic startup & manufacturing knowledge content (ideas, categories, resources).

Usage (from backend/ with venv active):
    python -m app.scripts.seed_content
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select

from app.db.base_models import Base
from app.db.session import SessionLocal, engine
from app.models.article import Article, ArticleDifficulty, ArticleStatus
from app.models.category import Category
from app.models.resource import Resource, ResourceType
from app.models.user import User, UserRole
from app.services.auth import AuthService
from app.core.config import get_settings
from app.utils.slug import estimate_reading_time, slugify

CATEGORIES = [
    {"name": "Artificial Intelligence", "slug": "artificial-intelligence", "description": "Generative AI, machine learning, synthetic data, and agentic LLM workflows.", "icon": "sparkles", "color": "#0369a1"},
    {"name": "Manufacturing & Industry 4.0", "slug": "manufacturing-industry-4-0", "description": "Factory automation, SMT assembly, CNC machining, and additive 3D manufacturing.", "icon": "cpu", "color": "#475569"},
    {"name": "Healthcare", "slug": "healthcare", "description": "Tele-ICU vitals telemetry, point-of-care diagnostics, AI radiology, and pharma dispensing.", "icon": "heart-pulse", "color": "#be123c"},
    {"name": "Agriculture", "slug": "agriculture", "description": "IoT soil analyzers, solar drip irrigation, cold storage telemetry, and hydroponics.", "icon": "sprout", "color": "#15803d"},
    {"name": "FinTech", "slug": "fintech", "description": "Merchant QR khata, supply chain credit scoring, invoice discounting, and embedded insurance.", "icon": "coins", "color": "#059669"},
    {"name": "EdTech", "slug": "edtech", "description": "AI adaptive tutoring, VR vocational labs, school attendance telemetry, and STEM vernacular.", "icon": "book-open", "color": "#2563eb"},
    {"name": "Clean Energy", "slug": "renewable-energy", "description": "Solar rooftop microgrids, biomass briquettes, second-life Li-ion packs, and micro-wind.", "icon": "zap", "color": "#eab308"},
    {"name": "Construction & Infrastructure", "slug": "construction-tech", "description": "Modular prefab buildings, drone site safety, eco-interlocking bricks, and concrete sensors.", "icon": "hammer", "color": "#78350f"},
    {"name": "Food Processing", "slug": "food-processing", "description": "Fruit powder processing, cold-pressed oil extraction, retort packaging, and millet snacks.", "icon": "utensils", "color": "#b45309"},
    {"name": "Robotics & Automation", "slug": "robotics", "description": "Autonomous mobile robots, agricultural drones, pipeline inspection, and robotic welding.", "icon": "bot", "color": "#7c3aed"},
    {"name": "Company Registration", "slug": "company-registration", "description": "Incorporate legally: private limited, LLP, OPC, and compliance kickoff.", "icon": "building", "color": "#1a6b4a"},
    {"name": "Funding", "slug": "funding", "description": "Bootstrapping, angels, VCs, grants, and term sheets for early teams.", "icon": "coins", "color": "#0f766e"},
    {"name": "GST", "slug": "gst", "description": "Goods and Services Tax registration, invoicing, returns, and credits.", "icon": "receipt", "color": "#b45309"},
    {"name": "Hiring", "slug": "hiring", "description": "Find, interview, and retain early talent without blowing the budget.", "icon": "users", "color": "#1d4ed8"},
    {"name": "Marketing", "slug": "marketing", "description": "Acquisition channels, funnels, content, and growth loops that work.", "icon": "megaphone", "color": "#be123c"},
]


CATEGORY_THUMBNAILS = {
    "artificial-intelligence": [
        "https://images.unsplash.com/photo-1677442136019-21780efad99a?auto=format&fit=crop&w=960&q=80",
        "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=960&q=80",
        "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=960&q=80",
    ],
    "manufacturing-industry-4-0": [
        "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=960&q=80",
        "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=960&q=80",
        "https://images.unsplash.com/photo-1581092335397-9583fe92d232?auto=format&fit=crop&w=960&q=80",
    ],
    "healthcare": [
        "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=960&q=80",
        "https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=960&q=80",
        "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?auto=format&fit=crop&w=960&q=80",
    ],
    "agriculture": [
        "https://images.unsplash.com/photo-1586771107445-d3ca888129ff?auto=format&fit=crop&w=960&q=80",
        "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?auto=format&fit=crop&w=960&q=80",
        "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?auto=format&fit=crop&w=960&q=80",
    ],
    "fintech": [
        "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=960&q=80",
        "https://images.unsplash.com/photo-1563986768494-4dee2763ff3f?auto=format&fit=crop&w=960&q=80",
    ],
    "edtech": [
        "https://images.unsplash.com/photo-1501504905252-473c47e087f8?auto=format&fit=crop&w=960&q=80",
        "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=960&q=80",
    ],
    "renewable-energy": [
        "https://images.unsplash.com/photo-1509391365360-2e959784a276?auto=format&fit=crop&w=960&q=80",
        "https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?auto=format&fit=crop&w=960&q=80",
    ],
    "construction-tech": [
        "https://images.unsplash.com/photo-1541888946425-d0fbb186a5b7?auto=format&fit=crop&w=960&q=80",
        "https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=960&q=80",
    ],
    "food-processing": [
        "https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=960&q=80",
        "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?auto=format&fit=crop&w=960&q=80",
    ],
    "robotics": [
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=960&q=80",
        "https://images.unsplash.com/photo-1581092335397-9583fe92d232?auto=format&fit=crop&w=960&q=80",
    ],
}


def _thumb(category_slug: str, seed: int) -> str:
    pool = CATEGORY_THUMBNAILS.get(category_slug, [
        "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=960&q=80"
    ])
    return pool[seed % len(pool)]



# Every subtopic has 3-4 distinct realistic ideas
SUBTOPIC_IDEAS_DATABASE = [
    # ── 1. ARTIFICIAL INTELLIGENCE ──────────────────────────────────────────
    # Subtopics: Legal AI, Code Security, Synthetic Data, Customer Copilot
    {
        "subtopic": "legal ai",
        "category_slug": "artificial-intelligence",
        "industry": "Artificial Intelligence",
        "items": [
            ("AI Legal Document Analyzer & Compliance Copilot", "₹6 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "SMEs spend hundreds of hours auditing commercial contracts.",
             "An automated RAG-powered LLM platform that ingests contracts, flags non-compliant clauses, and generates amendment drafts.",
             "Law firms, corporate legal teams, and startup founders.", "$28B global LegalTech market.",
             "Python, FastAPI, OpenAI GPT-4o, LangChain, ChromaDB.", "Fine-tuned domain models for Indian Companies Act.",
             "SaaS subscription starting at ₹4,999/month.", "Hallucination risks in legal interpretation.",
             "Month 1: Fine-tune legal parser. Month 2-3: Beta testing. Month 4+: Launch.", "Startup India Seed Fund, DPIIT Tax Exemption.", "MCA e-Courts Portal."),
            ("Automated Contract Clause & Regulatory Discovery Bot", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "Regulatory changes across state labor laws require constant monitoring.",
             "An AI agent that monitors government gazette notifications in real time and highlights impacted agreements.",
             "Corporate legal departments, CA firms, compliance agencies.", "$10B RegTech market.",
             "Python, LlamaIndex, PostgreSQL, React.", "Automated gazette scraping and semantic impact classification.",
             "Enterprise SaaS subscription at ₹12,000/month.", "OCR accuracy on scanned PDFs.",
             "Month 1-2: Scraper & NLP build. Month 3: Pilot. Month 4+: Sales.", "MeitY TIDE 2.0 Grant.", "Gazette of India."),
            ("Legal Discovery & Statutory Risk Assessment Engine", "₹8 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-high"],
             "Litigation lawyers lose billable hours sifting through court precedents.",
             "A semantic vector search engine trained on High Court judgments delivering precedent summaries in seconds.",
             "Litigation advocates, law firms, legal researchers.", "$5B legal search market.",
             "Python, Qdrant Vector DB, HuggingFace legal-BERT.", "Precedent relevance scoring and automated case headnotes.",
             "Per-lawyer subscription at ₹2,999/month.", "Multi-lingual judgment parsing.",
             "Month 1-2: Archive ingestion. Month 3: Advocate beta. Month 4+: Rollout.", "Startup India Recognition.", "Supreme Court e-Courts."),
        ]
    },
    {
        "subtopic": "code security",
        "category_slug": "artificial-intelligence",
        "industry": "Artificial Intelligence",
        "items": [
            ("Automated Code Security & API Vulnerability Scanner", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "Startups ship code with API flaws due to lack of security engineers.",
             "An AI code scanner that hooks into GitHub PRs and automatically generates unit test fixes for security breaches.",
             "DevOps engineers, CTOs, software teams.", "$12B DevSecOps market.",
             "Python, Rust AST parser, Semgrep, CodeLlama.", "Automated vulnerability patch generation.",
             "Freemium with $49/dev/month for private repos.", "Minimizing false positives.",
             "Month 1: AST scanner. Month 2: GitHub Action. Month 3+: Sales.", "MeitY TIDE 2.0 Grant.", "OWASP API Top 10."),
            ("AI Static Application Security Testing (SAST) Bot", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-high"],
             "Legacy SAST tools flood developers with non-exploitable false positives.",
             "A contextual AI SAST bot that evaluates production execution paths, filtering out noise.",
             "Enterprise engineering leads, FinTech developers.", "$3.5B SAST market.",
             "Go, Python, Semgrep AST, Tree-Sitter.", "Context-aware vulnerability triage neural net.",
             "B2B SaaS subscription at $199/team/month.", "Multi-language AST parsing.",
             "Month 1-2: Parser build. Month 3: Beta. Month 4+: Enterprise GTM.", "MeitY Cyber Grant.", "NIST Vulnerability DB."),
            ("Real-Time Dependency & Secret Exposure Guard", "₹5 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Accidental commits of AWS keys cause catastrophic cloud breaches.",
             "A pre-commit git hook & IDE plugin using ML entropy modeling to catch hardcoded secrets.",
             "Individual developers, agencies, software startups.", "$6B CSPM market.",
             "Rust CLI, Python ML Classifier, VS Code API.", "Entropy thresholding ML model for secret detection.",
             "Free open source; $12/user/month for team orgs.", "Sub-100ms git hook latency.",
             "Month 1: Rust CLI. Month 2: VS Code plugin. Month 3+: Dashboard.", "Digital India Initiative.", "GitGuardian Security Report."),
        ]
    },
    {
        "subtopic": "synthetic data",
        "category_slug": "artificial-intelligence",
        "industry": "Artificial Intelligence",
        "items": [
            ("Synthetic Data Generator for Healthcare Computer Vision", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-high"],
             "Medical AI startups face severe privacy constraints when training vision models.",
             "A generative diffusion model platform that outputs photorealistic, privacy-compliant synthetic X-rays.",
             "HealthTech startups, medical universities.", "$2.1B synthetic data market.",
             "PyTorch, Stable Diffusion, CUDA, FastAPI.", "Generative diffusion transformers for anomaly synthesis.",
             "Per-dataset generation fee (₹50,000 per 10k images).", "Ensuring medical anatomical fidelity.",
             "Month 1-2: Model training. Month 3-4: Validation. Month 5+: Licensing.", "BIRAC BIG Grant.", "NIH Chest X-ray Dataset."),
            ("Synthetic Customer Transaction Data Engine for FinTech", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "FinTech developers struggle to test fraud models without violating DPDP privacy.",
             "A tabular synthetic data engine generating privacy-safe financial transactions retaining distribution.",
             "Banks, NBFCs, FinTech credit startups.", "$1.5B financial synthetic market.",
             "Python, CTGAN, Differential Privacy Lib.", "Differential privacy math guarantees for transaction generation.",
             "Annual enterprise license at ₹3.5 Lakhs.", "Temporal transaction correlation.",
             "Month 1-2: Engine optimization. Month 3: Bank audit. Month 4+: Sales.", "RBI Innovation Hub Sandbox.", "RBI Data Guidelines."),
            ("Synthetic Industrial Video Dataset Generator for AI Training", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-high"],
             "Robotics teams cannot gather rare hazard video footage to train safety cameras.",
             "A 3D simulation synthetic dataset generator using Unreal Engine 5 rendering factory hazards.",
             "Robotics OEMs, vision integrators.", "$1.8B industrial vision market.",
             "Unreal Engine 5, Python API, NVIDIA Omniverse.", "Sim-to-real domain adaptation neural net.",
             "Custom dataset packages at ₹75,000 per 50k frames.", "Photorealistic render speeds.",
             "Month 1-2: 3D asset library. Month 3: Sim-to-real test. Month 4+: GTM.", "MeitY AI Mission Grant.", "NVIDIA Omniverse Docs."),
        ]
    },
    {
        "subtopic": "customer copilot",
        "category_slug": "artificial-intelligence",
        "industry": "Artificial Intelligence",
        "items": [
            ("E-Commerce AI Voice & WhatsApp Customer Support Copilot", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-high"],
             "D2C brands lose sales due to delayed response times on WhatsApp queries.",
             "An autonomous AI agent handling order tracking, returns, and recommendations 24/7.",
             "D2C brands, Shopify store owners.", "$18B conversational AI market.",
             "Node.js, Meta WhatsApp API, OpenAI GPT-4o-mini.", "Vernacular voice-to-text NLP for Hinglish messages.",
             "Monthly subscription at ₹2,999/month + ₹0.40/chat.", "Human agent handoff transitions.",
             "Month 1: WhatsApp bot. Month 2: Beta test. Month 3+: App store.", "Startup India Seed Fund.", "Shopify Developer Docs."),
            ("SaaS Multi-Channel Customer Success Agentic Copilot", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "B2B SaaS companies lose churned users who struggle with onboarding workflows.",
             "An AI copilot that monitors user session drop-offs and initiates guided in-app chat walk-throughs.",
             "B2B SaaS founders, customer success leads.", "$8B CS software market.",
             "React SDK, Python, LangChain, Pinecone.", "Churn propensity ML classifier predicting user exit.",
             "SaaS pricing at $99/month per product.", "SDK bundle size impact on web apps.",
             "Month 1-2: SDK & agent build. Month 3: Beta. Month 4+: SaaS launch.", "MeitY TIDE Grant.", "Gainsight CS Report."),
            ("Vernacular Retail Customer Engagement AI Assistant", "₹5 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-high"],
             "Local retail chains struggle to engage regional shoppers in native languages.",
             "A multilingual voice copilot for retail kiosks and mobile apps supporting 10 Indian languages.",
             "Retail chains, pharmacy networks.", "$5B retail tech market.",
             "Python, Bhabini AI API, Flutter, FastAPI.", "Speech-to-text ML in Tamil, Telugu, Hindi, Marathi.",
             "Kiosk licensing fee (₹1,500/kiosk/month).", "Noisy store audio environment filtering.",
             "Month 1: Language API integration. Month 2: Kiosk pilot. Month 3+: Sales.", "Digital India Bhabini Initiative.", "Bhabini Open AI Portal."),
        ]
    },

    # ── 2. MANUFACTURING & INDUSTRY 4.0 ────────────────────────────────────
    # Subtopics: PCB Assembly, Smart Factory, Predictive Maintenance, Industrial IoT, Textile Automation
    {
        "subtopic": "pcb assembly",
        "category_slug": "manufacturing-industry-4-0",
        "industry": "Manufacturing & Industry 4.0",
        "items": [
            ("Micro-Factory SMT Electronics PCB Assembly Line", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Hardware startups struggle with high MOQ penalties for small PCB assembly runs.",
             "A micro-factory setup equipped with desktop Pick-and-Place machines for quick-turn prototype assembly.",
             "IoT startups, robotics developers, EV makers.", "$100B EMS market.",
             "OpenPNP PnP machine, Desktop Reflow Oven, AOI Camera.", "Computer vision inspection for solder bridge defects.",
             "Turnkey assembly fees per board (₹150 to ₹800/board).", "Component inventory sourcing speed.",
             "Month 1: Benchtop PnP procurement. Month 2: Test runs. Month 3+: Local clients.", "PM MUDRA Scheme.", "IPC-A-610 Standard."),
            ("High-Density Surface Mount PCB Prototyping Bureau", "₹9 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Electronics engineers face 3-week delays importing double-sided 4-layer prototype boards.",
             "A localized PCB fabrication & SMT assembly service offering 48-hour turns for prototype boards.",
             "Aerospace hardware engineers, defense contractors.", "$16B rapid PCB market.",
             "CNC PCB Milling Machine, SMT Pick & Place, Reflow Oven.", "Gerber file AI pre-flight error checker.",
             "Per-board prototyping charges starting at ₹1,200.", "Chemical bath waste disposal.",
             "Month 1-2: Equipment setup. Month 3: Beta orders. Month 4+: Scaling.", "SPECS Electronics Scheme.", "IPC-2221 Standard."),
            ("Automated Desktop Soldering & PCB Assembly Station", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Small makers struggle with manual THT/SMT soldering quality control.",
             "A benchtop 4-axis robotic soldering station with automatic wire feeding.",
             "Educational labs, IoT device assembly workshops.", "$4B soldering automation market.",
             "4-Axis Stepper Rig, PID Soldering Controller, OpenCV.", "Vision-guided solder point location.",
             "Unit sales of benchtop soldering robots (₹1.8 Lakh).", "Tip oxide clean maintenance.",
             "Month 1: Mechanical rig build. Month 2: Vision calibration. Month 3+: Sales.", "MSME Udyam Scheme.", "IPC J-STD-001."),
        ]
    },
    {
        "subtopic": "smart factory",
        "category_slug": "manufacturing-industry-4-0",
        "industry": "Manufacturing & Industry 4.0",
        "items": [
            ("Modular Smart Factory Execution System (MES)", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "Medium manufacturing plants rely on paper job cards, leading to inaccurate OEE tracking.",
             "A lightweight cloud MES connected to wireless shop-floor tablets providing real-time OEE metrics.",
             "Auto components factories, plastics molding plants.", "$24B MES market.",
             "Node.js, PostgreSQL, MQTT Broker, Android Tablets.", "Production line balancing algorithms.",
             "Factory SaaS subscription at ₹15,000/month per line.", "Shop-floor operator digital adoption.",
             "Month 1-2: Tablet app build. Month 3: Pilot trial. Month 4+: Sales.", "MSME Innovation Scheme.", "ISA-95 MES Standard."),
            ("Industrial Computer Vision Quality Control Rig", "₹8 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-high"],
             "Manual visual inspection on high-speed conveyor belts misses micro-cracks and flaws.",
             "An inline optical inspection conveyor rig equipped with Edge AI models that eject defective parts.",
             "Pharma bottle plants, auto stamping suppliers.", "$11B machine vision market.",
             "Jetson Orin Nano, Industrial Camera, OpenCV, PyTorch.", "Sub-millimeter anomaly detection at 300 PPM.",
             "Hardware rig fee (₹4.5 Lakhs) + monthly maintenance.", "Reflective metal lighting calibration.",
             "Month 1-2: Optical rig integration. Month 3: Pilot. Month 4+: Machine sales.", "SAMARTH Udyog 4.0.", "ISO 9001 Quality Standard."),
            ("Smart Factory Energy Audit & Power Telemetry Controller", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Factories suffer from high electricity bills due to unmonitored idle machine power draw.",
             "IoT smart energy meters installed on distribution panels logging power factor and peak demand.",
             "Textile mills, forging units, cold storages.", "$15B energy management market.",
             "MODBUS RS485 Energy Meters, ESP32 Gateway, Grafana.", "Peak load demand forecasting AI model.",
             "Hardware installation fee + 15% shared energy savings.", "CT clamp installation safety.",
             "Month 1: Energy meter gateway setup. Month 2: Factory trial. Month 3+: Commercial GTM.", "BEE Energy Efficiency Scheme.", "ISO 50001 Energy Standard."),
        ]
    },
    {
        "subtopic": "predictive maintenance",
        "category_slug": "manufacturing-industry-4-0",
        "industry": "Manufacturing & Industry 4.0",
        "items": [
            ("Smart Factory Industrial Equipment Maintenance Sensor Node", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "Unplanned machine downtime costs manufacturing plants millions in lost production.",
             "Magnetic plug-and-play tri-axial vibration and thermal sensors transmitting live FFT telemetry.",
             "Textile mills, food processing plants, auto parts factories.", "$14B predictive maintenance market.",
             "STM32 MCU, MEMS Accelerometers, LoRaWAN, Python.", "Edge AI vibration spectrum anomaly detection.",
             "Hardware node fee (₹4,500) + monthly SaaS (₹999/machine).", "Factory electromagnetic noise isolation.",
             "Month 1-2: Sensor hardware & firmware. Month 3: Pilot. Month 4+: Rollout.", "ATUFS Scheme.", "ISO 10816 Vibration Standard."),
            ("Motor Vibration & Acoustic Anomaly Diagnostic System", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-high"],
             "Industrial electric motors experience sudden rotor imbalance burning out windings.",
             "A clamp-on acoustic emission microphone and current signature analyzer identifying motor health.",
             "Water pumping stations, HVAC plants, cement mills.", "$8B motor monitoring market.",
             "ESP32, Acoustic Sensor, CT Clamp, Python ML.", "Motor Current Signature Analysis (MCSA) neural net.",
             "Diagnostic hardware (₹18,000) + monthly software.", "Background factory noise filtering.",
             "Month 1: Prototype build. Month 2: Pump house trials. Month 3+: Sales.", "National Motor Efficiency Scheme.", "IEEE 1415 Maintenance Standard."),
            ("Hydraulic Press & Gearbox Predictive Failure Detector", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "Hydraulic oil contamination and gear wear cause sudden press downtime.",
             "Oil viscosity & particle counter sensors paired with gear mesh frequency AI analysis.",
             "Stamping units, plastic injection molders.", "$6B hydraulic diagnostics market.",
             "Oil Optical Sensor, Vibration Node, Node.js, Grafana.", "Oil degradation & wear particle classification ML.",
             "Sensor kit sale (₹28,000/press) + annual SaaS.", "Sensor oil pressure rating clearance.",
             "Month 1-2: Sensor manifold build. Month 3: Stamping plant test. Month 4+: Rollout.", "MSME Credit Guarantee Scheme.", "ISO 4406 Cleanliness Code."),
        ]
    },
    {
        "subtopic": "industrial iot",
        "category_slug": "manufacturing-industry-4-0",
        "industry": "Manufacturing & Industry 4.0",
        "items": [
            ("Cellular NB-IoT Industrial Gateway & Sensor Hub", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Remote factory machinery lacks reliable Wi-Fi for cloud data logging.",
             "A ruggedized IP67 RS485/Modbus to NB-IoT/4G cellular gateway streaming telemetry to AWS IoT.",
             "Pump manufacturers, generator operators, solar farms.", "$18B industrial IoT market.",
             "ESP32-S3, Quectel NB-IoT Module, MODBUS, AWS IoT Core.", "Edge telemetry data compression & store-and-forward.",
             "Gateway sale (₹6,500/unit) + SIM data SaaS fee.", "Cellular signal reception in basements.",
             "Month 1: Hardware PCB & enclosure. Month 2: Field test. Month 3+: B2B distributor sales.", "MeitY IoT Framework.", "3GPP NB-IoT Standards."),
            ("Wireless Factory Environment Monitoring System", "₹5 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Pharma and electronics plants must log cleanroom temperature, humidity, and dust continuously.",
             "LoRaWAN wireless sensor nodes monitoring Temp/RH/PM2.5 with automated SMS breach alerts.",
             "Pharma cleanrooms, semiconductor labs, food plants.", "$9B environmental IoT market.",
             "Sensirion Humidity Sensor, LoRaWAN Node, Gateway, React.", "Predictive HVAC cooling load regulation algorithm.",
             "Node kit (₹3,200) + monthly audit compliance SaaS.", "Cleanroom sensor calibration certification.",
             "Month 1: LoRa sensor node build. Month 2: Pharma lab trial. Month 3+: Sales.", "FDA 21 CFR Part 11 Compliance.", "ISO 14644 Cleanroom Standard."),
            ("Industrial RFID Equipment Tracking & Audit Node", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Large factories lose track of expensive tooling, dies, and movable equipment.",
             "UHF long-range RFID readers mounted on factory gates tracking tagged assets automatically.",
             "Auto assembly plants, heavy machinery shops.", "$12B industrial RFID market.",
             "UHF RFID Reader, Impinj Tags, Node.js, PostgreSQL.", "Asset movement route anomaly detection.",
             "Hardware portal installation + annual software license.", "Metal interference with RFID signals.",
             "Month 1-2: UHF RFID antenna tuning. Month 3: Plant pilot. Month 4+: Sales.", "Make in India Incentive.", "EPCglobal Gen2 RFID Standard."),
        ]
    },
    {
        "subtopic": "textile automation",
        "category_slug": "manufacturing-industry-4-0",
        "industry": "Manufacturing & Industry 4.0",
        "items": [
            ("Automated Cloth Fabric Defect Computer Vision Inspection", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "Manual fabric inspection in textile weaving mills misses 30% of micro-defects.",
             "A high-speed optical camera frame scanning running fabric rolls at 60m/min and tagging defects in real-time.",
             "Textile weaving mills, garment exporters, dyeing units.", "$1.5T global textile industry.",
             "Line Scan Camera, NVIDIA Jetson Orin Nano, OpenCV, PyTorch.", "YOLOv8 deep learning model classifying 20+ fabric defects.",
             "Inspection rig installation (₹3.5 Lakhs) + monthly fee.", "Handling high-speed motion blur.",
             "Month 1-2: Optical hardware build. Month 3: Mill trial. Month 4+: Mill deployment.", "ATUFS Textile Grant.", "ASTM D3990 Defect Standard."),
            ("Smart Loom Thread Tension Monitoring Sensor", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Unnoticed thread snapping on power looms causes long fabric weaving downtime.",
             "Piezoelectric yarn tension sensors installed on loom threads that stop the motor instantly upon snap.",
             "Power loom clusters, silk weaving units.", "$4B textile machinery market.",
             "Piezo Sensors, STM32 MCU, Wireless Mesh, Relay Cutoff.", "Yarn tension wave pattern anomaly detection.",
             "Sensor bar sale per loom (₹4,500/loom line).", "Lint and dust accumulation on sensors.",
             "Month 1: Sensor bar prototype. Month 2: Power loom cluster trial. Month 3+: Cluster sales.", "Samarth Scheme for Textile.", "Textile Committee Quality Guide."),
            ("Automated Dyeing Color Match & Recipe Dispenser", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "Textile dyeing units suffer batch-to-batch shade mismatch resulting in fabric waste.",
             "A spectrophotometer liquid color matcher that formulates exact dye recipes automatically.",
             "Dyeing houses, fabric processing units.", "$6B textile processing market.",
             "Spectrophotometer, Peristaltic Dosing Pumps, Python, React.", "Neural net color formulation matching target Delta-E.",
             "Dosing machine sale (₹2.8 Lakhs) + dye recipe software.", "Peristaltic tube chemical wear.",
             "Month 1-2: Spectrophotometer & dosing build. Month 3: Dye house trial. Month 4+: Sales.", "ATUFS Textile Scheme.", "ISO 105 Color Fastness Standard."),
        ]
    },

    # ── 3. HEALTHCARE ───────────────────────────────────────────────────────
    # Subtopics: Telemedicine, Remote Monitoring, Medical Devices, AI Diagnostics
    {
        "subtopic": "telemedicine",
        "category_slug": "healthcare",
        "industry": "Healthcare",
        "items": [
            ("Vernacular Telemedicine & Remote Consultation Platform", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Rural patients travel 50km to reach specialist doctors for basic consultations.",
             "A low-bandwidth video & WhatsApp telemedicine platform connecting rural clinics with urban specialist doctors.",
             "Rural clinics, general practitioners, pharmacy stores.", "$5.4B Indian telemedicine market.",
             "Flutter, WebRTC, Node.js, ABDM Health ID Integration.", "Vernacular voice symptom intake assistant.",
             "Per-consultation platform fee (₹30 - ₹75 per session).", "Unstable rural internet connections.",
             "Month 1-2: App build & ABDM Sandbox. Month 3: Rural clinic pilot. Month 4+: Scaling.", "ABDM Incentive Scheme.", "Telemedicine Guidelines India."),
            ("Rural Tele-Clinic Kiosk & Prescription Station", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Village healthcare centers lack diagnostic tools for remote doctor visits.",
             "An integrated kiosk with blood pressure, SpO2, ECG, and thermal printer for instant tele-prescriptions.",
             "Gram panchayats, rural entrepreneurs, NGO health centers.", "$8B rural health market.",
             "Touch Kiosk, Medical Sensors, Node.js, WhatsApp API.", "Automated triage classification based on vitals.",
             "Kiosk sale (₹85,000/kiosk) + subscription per consultation.", "Kiosk maintenance in remote villages.",
             "Month 1-2: Kiosk assembly & sensor integration. Month 3: Panchayat pilot. Month 4+: Rollout.", "National Health Mission.", "CDSCO Medical Device Rules."),
            ("Specialty Tele-Consultation & E-ICU Bridge", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-high"],
             "Small nursing homes struggle to get instant cardiologist and neurologist opinions.",
             "A real-time high-definition video & telemetry bridge streaming diagnostic wave Data to on-call specialists.",
             "Small hospitals (10-50 beds), nursing homes.", "$6B e-ICU market.",
             "WebRTC, C++, DICOM Viewer, Node.js, WebSockets.", "AI ECG rhythm arrhythmia alert system.",
             "Hospital monthly fee (₹8,000/month per active ward).", "Sub-200ms latency video telemetry.",
             "Month 1-2: HD WebRTC bridge engine. Month 3: Hospital trial. Month 4+: Scaling.", "ABDM Integration Fund.", "IEEE Health Informatics."),
        ]
    },
    {
        "subtopic": "remote monitoring",
        "category_slug": "healthcare",
        "industry": "Healthcare",
        "items": [
            ("Remote Patient Vital Monitoring & Tele-ICU Platform", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "Tier-2 city hospitals lack specialized ICU doctors, leading to high post-operative mortality rates.",
             "An IoT bedside monitor gateway streaming ECG, SpO2, NIBP, and temperature data to a central command center.",
             "Small hospitals, nursing homes, home ICU care.", "$22% CAGR remote monitoring market.",
             "Medical Sensors, ESP32-S3, MQTT Broker, Node.js, WebRTC.", "Early warning score neural net predicting cardiac arrest.",
             "Hospital subscription at ₹1,500/bed/month.", "Zero data dropouts during internet fluctuations.",
             "Month 1: Prototype gateway. Month 2-3: Hospital pilot. Month 4+: Commercial scaling.", "ABDM Integration Grant.", "Telemedicine Guidelines 2020."),
            ("Wearable Continuous Cardiac & Pulse Telemetry Patch", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-high"],
             "Post-cardiac surgery patients are discharged without continuous heart monitoring at home.",
             "A chest-worn Bluetooth ECG patch logging arrhythmia events and sending family alerts.",
             "Cardiologists, post-op cardiac patients, senior care.", "$10B cardiac wearable market.",
             "Single-lead ECG Sensor, BLE MCU, iOS/Android App, AWS.", "Atrial fibrillation detection neural network.",
             "Patch device sale (₹6,500) + monthly monitoring subscription.", "Skin adhesive biocompatibility.",
             "Month 1-2: Patch hardware & ECG circuit. Month 3: Clinical testing. Month 4+: Hospital sales.", "BIRAC BIG Grant.", "ISO 10993 Biocompatibility."),
            ("Post-Operative Home ICU Telemetry Gateway", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Families paying ₹15,000/day for hospital ICU beds want safe home recovery options.",
             "A portable home ICU gateway connecting oxygen, blood pressure, and pulse vitals to doctor dashboards.",
             "Home healthcare agencies, post-op recovery patients.", "$7B home health market.",
             "Raspberry Pi 4, BLE Health Sensors, Node.js, React.", "Vitals stability trend prediction algorithm.",
             "Gateway monthly rental (₹4,500/month).", "Family member sensor application errors.",
             "Month 1-2: Gateway software & BLE stack. Month 3: Home care trial. Month 4+: Agency rollout.", "National Health Mission.", "ABDM Health Policy."),
        ]
    },
    {
        "subtopic": "medical devices",
        "category_slug": "healthcare",
        "industry": "Healthcare",
        "items": [
            ("Portable Diagnostic Point-of-Care Blood Testing Device", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-hybrid"],
             "Rural clinics wait 24-48 hours for basic CBC and HbA1c blood test results from central labs.",
             "A microfluidic cartridge handheld spectrophotometer delivering blood parameters in 5 minutes via Bluetooth.",
             "Primary healthcare centers, home labs, general practitioners.", "$45B Point-of-Care market.",
             "Microfluidic Test Strip, Photodiode Array, ARM MCU, Flutter.", "ML curve fitting for colorimetric reaction analysis.",
             "Hardware reader sale (₹25,000) + test cartridges (₹80/unit).", "CDSCO Class B clearance approval.",
             "Month 1-3: Cartridge design. Month 4-5: Clinical validation. Month 6: Regulatory filing.", "BIRAC BIG Scheme.", "CDSCO Medical Device Rules."),
            ("Handheld Microfluidic HbA1c & Lipid Analyzer", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Diabetic patients in rural areas lack quick HbA1c testing for medication adjustment.",
             "A finger-prick microfluidic test meter giving HbA1c percentage results in 3 minutes.",
             "Diabetes clinics, pharmacies, path labs.", "$12B diabetes diagnostic market.",
             "Microfluidic Disc, LED Optical Sensor, STM32, Android App.", "Calibration curve drift compensation ML.",
             "Device price (₹16,000) + test strip margin.", "Test strip enzyme shelf life stability.",
             "Month 1-2: Optical meter & disc build. Month 3: Clinical comparison test. Month 4+: Distribution.", "BIRAC SPARSH Grant.", "WHO Diabetes Diagnostic Guide."),
            ("Non-Invasive Photometric Oxygen & Hemoglobin Monitor", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Anemic pregnant women require frequent blood draws to monitor hemoglobin levels.",
             "A non-invasive multi-wavelength finger clip measuring total hemoglobin optically without needles.",
             "Maternal health clinics, anemia screening camps.", "$5B non-invasive sensor market.",
             "Multi-Wavelength LED Array, Photodiode, ESP32, Flutter.", "Photoplethysmography (PPG) signal extraction model.",
             "Unit device sale (₹12,000/unit) to health centers.", "Skin pigmentation optical interference.",
             "Month 1-2: PPG sensor circuit & optical array. Month 3: Clinic trial. Month 4+: Camp sales.", "National Health Mission Anemia Scheme.", "CDSCO Device Guidelines."),
        ]
    },
    {
        "subtopic": "ai diagnostics",
        "category_slug": "healthcare",
        "industry": "Healthcare",
        "items": [
            ("AI Radiology Screening & Chest X-Ray Triage Copilot", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "Radiologist shortages cause severe delays in identifying critical lung infections and TB.",
             "A DICOM-compliant computer vision AI service screening chest X-rays for pneumothorax and TB in 10 seconds.",
             "Diagnostic radiology centers, government TB programs.", "$14B AI medical imaging market.",
             "PyTorch, TorchVision ResNet, Orthanc DICOM, FastAPI.", "Deep CNN trained on 100,000+ chest radiographies.",
             "Pay-per-scan API model (₹40 per processed scan).", "Achieving 95%+ sensitivity without false negatives.",
             "Month 1-2: Model training. Month 3: Clinical validation. Month 4+: Adoption.", "BIRAC SPARSH Grant.", "CDSCO AI Medical Guidelines."),
            ("Derm-AI Skin Lesion Scanner & Diagnostic Assistant", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-high"],
             "Patients wait months for dermatologist appointments to check suspicious moles.",
             "A mobile dermatoscope lens attachment & AI app analyzing skin lesions for melanoma risk.",
             "Dermatologists, general practitioners, pharmacies.", "$4B AI dermatology market.",
             "Dermatoscope Optic Attachment, TensorFlow Lite, Flutter.", "CNN skin cancer classification model.",
             "Lens attachment sale (₹4,500) + app subscription.", "Lighting glare artifact removal.",
             "Month 1: Lens design & TFLite model. Month 2: Clinical trial. Month 3+: GP sales.", "Startup India Seed Fund.", "Dermatology AI Benchmarks."),
            ("AI Diabetic Retinopathy Diagnostic Camera System", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-high"],
             "Diabetic patients suffer preventable blindness due to unmonitored retinal micro-aneurysms.",
             "A portable fundus camera equipped with offline AI screening retinal images for diabetic retinopathy.",
             "Eye clinics, diabetes centers, mobile vision vans.", "$6B ophthalmology diagnostic market.",
             "Fundus Camera Lens, Jetson Orin, PyTorch, React.", "EfficientNet retina lesion grading model.",
             "Camera unit sale (₹1.4 Lakhs) + cloud backup SaaS.", "Pupil dilation image clarity requirements.",
             "Month 1-2: Fundus camera & model integration. Month 3: Vision camp pilot. Month 4+: Sales.", "National Programme for Control of Blindness.", "AI Ophthalmology Guidelines."),
        ]
    },

    # ── 4. AGRICULTURE ──────────────────────────────────────────────────────
    # Subtopics: Precision Farming, Smart Irrigation, Cold Storage, Soil Health
    {
        "subtopic": "precision farming",
        "category_slug": "agriculture",
        "industry": "Agriculture",
        "items": [
            ("Multispectral Satellite & Drone Precision Crop Health Platform", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-high"],
             "Farmers detect pest stress too late, losing 20-30% of harvest yield.",
             "A satellite and drone imaging platform computing NDVI maps to pinpoint field stress zones.",
             "FPOs, sugarcane mills, crop insurers.", "$16B precision ag market.",
             "Sentinel-2 API, Python GDAL, OpenCV, Flutter, Firebase.", "Deep learning crop stress prediction model.",
             "Per-acre annual SaaS subscription (₹120/acre/year).", "Monsoon cloud cover interference.",
             "Month 1-2: Satellite pipeline. Month 3: FPO pilot. Month 4+: Commercial scaling.", "RKVY-RAFTAAR Grant.", "ISRO VEDAS Portal."),
            ("Precision Variable-Rate Fertilizer Application Controller", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Uniform fertilizer spreading wastes expensive chemicals in nutrient-rich soil patches.",
             "A tractor-mounted variable-rate controller adjusting fertilizer drop rate based on live GPS soil maps.",
             "Tractor owners, custom hiring centers, large farms.", "$8B precision farming hardware market.",
             "GPS Receiver, Stepper Motor Actuator, Arduino, Android App.", "GIS prescription map parsing algorithm.",
             "Controller attachment sale (₹22,000/unit).", "Tractor vibration dust resistance.",
             "Month 1-2: Mechanical controller & GPS parser. Month 3: Field test. Month 4+: Sales.", "Sub-Mission on Agri Mechanization.", "ICAR Precision Ag Guidelines."),
            ("Precision Micro-Climate Weather Telemetry Station", "₹5 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Regional weather forecasts lack hyperlocal accuracy for frost and pest disease warnings.",
             "A solar-powered farm weather station logging temp, humidity, leaf wetness, and wind speed.",
             "Grape growers, tea gardens, apple orchards.", "$5B ag weather market.",
             "Anemometer, Rain Gauge, Sensirion Sensors, ESP32, Cellular.", "Fungal disease outbreak prediction model.",
             "Weather station sale (₹14,000) + SMS alert SaaS.", "Sensor calibration in extreme rainfall.",
             "Month 1: Station assembly & sensors. Month 2: Orchard trial. Month 3+: Dealer sales.", "RKVY-RAFTAAR Scheme.", "IMD Agromet Advisory Portal."),
        ]
    },
    {
        "subtopic": "smart irrigation",
        "category_slug": "agriculture",
        "industry": "Agriculture",
        "items": [
            ("Automated Solar-Powered Drip Smart Irrigation Controller", "₹5 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Farmers waste groundwater running irrigation pumps on fixed timers.",
             "A solar-powered IoT valve controller turning drip irrigation on/off based on real-time soil moisture.",
             "Drip irrigated orchards, polyhouse owners.", "$15% CAGR smart irrigation market.",
             "ESP32, Soil Moisture Sensor, Solenoid Valve, 10W Solar Panel.", "Evapotranspiration ML model predicting water deficit.",
             "Hardware unit sale (₹8,500/valve) + app subscription.", "Solenoid valve mineral scale clogging.",
             "Month 1: Valve controller build. Month 2: Polyhouse pilot. Month 3+: Dealer distribution.", "PMKSY Drip Subsidy.", "FAO Irrigation Paper 56."),
            ("Soil Moisture & Soil Matrix Smart Irrigation Valve", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Deep root crops like pomegranate require sub-surface moisture sensing at different soil depths.",
             "Dual-depth soil matric potential sensors communicating with a wireless smart irrigation manifold.",
             "Pomegranate, grape, and citrus fruit growers.", "$6B orchard irrigation market.",
             "Tensiometer Sensors, LoRaWAN Node, Latching Valve, React.", "Root zone moisture absorption modeling.",
             "Valve manifold kit (₹12,500) + mobile app.", "Tensiometer ceramic tip maintenance.",
             "Month 1-2: Sensor manifold build. Month 3: Orchard trial. Month 4+: Sales.", "MIDH Horticulture Subsidy.", "ICAR Water Management Guide."),
            ("Subsurface Smart Irrigation Telemetry Node", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Surface drip lines get damaged by rodent bites and farm tilling equipment.",
             "Subsurface drip irrigation telemetry nodes buried 30cm underground monitoring root hydration.",
             "Sugarcane farmers, cotton growers, commercial farms.", "$7B subsurface drip market.",
             "IP68 Underground Sensors, NB-IoT Module, Sealed Battery.", "Subsurface water infiltration rate calculation.",
             "Underground sensor node sale (₹4,800/node).", "Underground wireless signal attenuation.",
             "Month 1-2: IP68 node waterproofing & antenna. Month 3: Sugarcane test. Month 4+: Sales.", "PMKSY Scheme.", "Sugarcane Research Institute Manual."),
        ]
    },
    {
        "subtopic": "cold storage",
        "category_slug": "agriculture",
        "industry": "Agriculture",
        "items": [
            ("Micro Solar Cold Storage Room for Perishable Produce", "₹9 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-non-ai"],
             "Small farmers face post-harvest price crashes because fruits spoil within 48 hours.",
             "A 5-metric-ton walk-in solar cold room utilizing thermal battery storage to maintain 4°C without grid power.",
             "Farmer cooperatives, vegetable mandis, berry farmers.", "$250B cold storage market.",
             "R404a Unit, Phase Change Material (PCM), 3kW Solar Array, PUF Panels.", "Thermal battery charge optimization during peak solar.",
             "Cold room sale (₹7.5 Lakhs) or storage fee (₹15/crate/day).", "Insulation leak prevention in summer.",
             "Month 1-2: PUF assembly & PCM test. Month 3: Farm-gate deployment. Month 4+: FPO sales.", "MIDH 35-50% Subsidy.", "NCCD Cold Chain Guidelines."),
            ("IoT Cold Storage Temperature & Humidity Telemetry Beacon", "₹4 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Cold storage operators suffer inventory rot when refrigeration compressors fail unnoticed at night.",
             "Wireless BLE/Cellular temperature beacons logging thermal stability and sending phone alert calls.",
             "Cold storage owners, pharma distributors, fruit exporters.", "$4B cold chain IoT market.",
             "NIST Calibrated Temp Sensor, Cellular Module, Battery, React.", "Thermal breakdown alert prediction algorithm.",
             "Beacon hardware sale (₹3,500/unit) + monthly monitoring.", "Sensor calibration in -20°C environments.",
             "Month 1: Beacon hardware build. Month 2: Cold store trial. Month 3+: Sales.", "MIDH Cold Chain Scheme.", "FSSAI Storage Regulations."),
            ("Portable Phase-Change Material (PCM) Agri Transport Cooler", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Small fruit growers cannot afford refrigerated trucks for transporting high-value berries to city markets.",
             "Insulated PCM transport boxes maintaining 2-8°C for 36 hours inside standard cargo vehicles.",
             "Strawberry farmers, florists, dairy distributors.", "$5B passive cooling market.",
             "Rotomolded Outer Box, Eutectic PCM Plates, Temp Logger.", "PCM latent heat absorption optimization.",
             "Cooler box sale (₹18,000 per 100L box).", "PCM freezing cycle time before transit.",
             "Month 1: Mold design & PCM formulation. Month 2: Transit test. Month 3+: Farmer sales.", "PMFME Agri Scheme.", "APEDA Export Guidelines."),
        ]
    },
    {
        "subtopic": "soil health",
        "category_slug": "agriculture",
        "industry": "Agriculture",
        "items": [
            ("IoT Soil Health & Real-Time NPK Nutrient Analyzer", "₹4 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Farmers over-fertilize crops based on guesswork, leading to soil degradation.",
             "A portable optical soil probe measuring Nitrogen, Phosphorus, Potassium (NPK), pH, and moisture in 60 seconds.",
             "Farmers, agri extension officers, fertilizer dealers.", "$24B agritech market.",
             "Optical Spectrometry Sensor, ESP32 BLE, Android App.", "Crop-specific ML fertilizer recommendation algorithms.",
             "Device sales (₹7,500/unit) + SaaS report fees.", "Calibrating optical sensors across clay/sandy soils.",
             "Month 1: Prototype soil probe. Month 2: KVK trials. Month 3+: Commercial launch.", "RKVY-RAFTAAR Grant.", "Soil Health Card Scheme."),
            ("Rapid Electrochemical Soil Carbon & Micronutrient Tester", "₹6 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Organic farming certification requires lab soil organic carbon tests that take weeks.",
             "An electrochemical soil sensor measuring Soil Organic Carbon (SOC) and zinc/boron micronutrients in 3 minutes.",
             "Organic farmers, carbon credit certifiers, tea estates.", "$3B soil carbon market.",
             "Electrochemical Ion Sensors, Microfluidic Chip, Flutter.", "Soil organic carbon regression model.",
             "Tester unit price (₹22,000) + test reagent packs.", "Electrode degradation in high-salinity soils.",
             "Month 1-2: Electrochemical chip build. Month 3: Lab validation. Month 4+: Certification sales.", "PKVY Organic Farming Scheme.", "ICAR Soil Carbon Guidelines."),
            ("Portable Spectroscopic Soil Salinity & pH Monitor", "₹5 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Saline water irrigation damages soil electrical conductivity (EC), ruining crop roots.",
             "A rugged handheld probe measuring Soil EC, pH, and TDS for instant irrigation salinity management.",
             "Coastal farmers, shrimp farm operators, greenhouse growers.", "$2B soil salinity market.",
             "Four-Electrode EC Sensor, Glass pH Electrode, ESP32.", "Soil salinity crop tolerance index algorithm.",
             "Probe sale (₹9,500/unit) + mobile app.", "pH glass bulb field breakage protection.",
             "Month 1: EC/pH probe build. Month 2: Coastal field test. Month 3+: Dealer distribution.", "Soil Health Card Programme.", "ICAR Salinity Research Guide."),
        ]
    },

    # ── 5. FINTECH ──────────────────────────────────────────────────────────
    # Subtopics: Micro Khata, Credit Scoring, Invoice Discounting, Embedded Insurance
    {
        "subtopic": "micro khata",
        "category_slug": "fintech",
        "industry": "FinTech",
        "items": [
            ("Micro-Merchant QR Payment & Automated Khata SaaS", "₹5 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Kirana stores lose revenue due to uncollected customer credit (Udhar) and paper ledger errors.",
             "A vernacular app combining UPI QR payments with automated WhatsApp payment reminder links.",
             "Kirana shopkeepers, street vendors, pharmacy stores.", "60M+ Indian MSMEs digitizing.",
             "Flutter, Node.js, PostgreSQL, UPI Stack, WhatsApp API.", "ML cash-flow credit scoring algorithms for micro-loans.",
             "MDR-free basic tier + micro-loan distribution fee.", "Merchant willingness to pay upfront.",
             "Month 1-2: App & UPI build. Month 3: Market acquisition. Month 4+: Lending partnership.", "Digital India Initiative.", "NPCI UPI Specifications."),
            ("Digital Credit Khata & Udhar Recovery WhatsApp Bot", "₹4 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Small shops hesitate to send manual credit recovery messages to local customers.",
             "An automated WhatsApp bot sending polite localized payment links and partial installment plans.",
             "Local retail merchants, garment shops, hardware stores.", "$4B merchant SaaS market.",
             "Python, Meta WhatsApp API, UPI Deep Links, React.", "Polite conversational AI negotiation prompt templates.",
             "Subscription pricing at ₹199/month per merchant.", "WhatsApp message template approval.",
             "Month 1: WhatsApp bot. Month 2: Merchant beta. Month 3+: Scaling.", "SIDBI Micro-Lending Scheme.", "RBI Digital Payment Guide."),
            ("Vernacular Merchant Multi-Store Khata Ledger", "₹6 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Merchants operating 2-3 small branches struggle to consolidate cash flows and stock credit.",
             "A multi-store digital khata ledger supporting voice entry in Hindi, Tamil, and Gujarati.",
             "Multi-branch Kirana stores, wholesale distributors.", "$5B retail ledger market.",
             "Flutter, Bhabini Voice API, Node.js, PostgreSQL.", "Voice-to-ledger NLP converting spoken sales to entries.",
             "Multi-store subscription at ₹499/month.", "Voice recognition accuracy in noisy shops.",
             "Month 1-2: Multi-store ledger & voice engine. Month 3: Market trial. Month 4+: Scaling.", "Digital India Bhabini.", "NPCI Merchant API."),
        ]
    },
    {
        "subtopic": "credit scoring",
        "category_slug": "fintech",
        "industry": "FinTech",
        "items": [
            ("Alternative Cash-Flow Credit Scoring Engine for MSMEs", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "Banks reject 70% of MSME loans due to lack of collateral and credit history.",
             "An API engine analyzing GST returns, bank statements, and UPI velocity to generate instant credit scores.",
             "NBFCs, digital lending apps, neo-banks.", "$350B MSME credit gap.",
             "Python, Account Aggregator API, XGBoost ML Model.", "ML fraud score model identifying circular GST transactions.",
             "Per-API call underwriting fee (₹45 to ₹120 per report).", "Model calibration across economic cycles.",
             "Month 1-2: AA API & ML training. Month 3: NBFC sandbox. Month 4+: API scaling.", "RBI Account Aggregator Framework.", "Sahamati AA Standards."),
            ("GST & Invoice Underwriting Credit Assessment API", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-high"],
             "Lenders take 2 weeks to manually verify vendor GST filing consistency and tax compliance.",
             "An automated GSTN API crawler scoring vendor tax filing discipline and invoice authenticity.",
             "Supply chain lenders, invoice discounting platforms.", "$10B credit underwriting tech market.",
             "Python, GSTN API, FastAPI, PostgreSQL.", "GST turnover discrepancy neural net classifier.",
             "API call pricing at ₹30 per GST verification.", "GST portal API rate limits.",
             "Month 1-2: GSTN API engine. Month 3: Lender pilot. Month 4+: Commercial scaling.", "GSTN Developer Portal.", "RBI Digital Lending Guide."),
            ("Supply Chain Financial Credit Risk Scoring Platform", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "Corporate buyers cannot assess tier-2/tier-3 vendor insolvency risks in advance.",
             "A credit risk monitoring platform evaluating supplier financial health using public filings and trade credit history.",
             "Auto OEMs, large manufacturers, corporate buyers.", "$8B supply chain risk market.",
             "Node.js, Python, MCA API, React Dashboard.", "Predictive supplier bankruptcy risk scoring algorithm.",
             "Corporate SaaS license (₹25,000/month per procurement department).", "Incomplete MCA filing records.",
             "Month 1-2: MCA API scraper & risk model. Month 3: Corporate trial. Month 4+: Sales.", "Startup India Recognition.", "MCA Data Portal."),
        ]
    },
    {
        "subtopic": "invoice discounting",
        "category_slug": "fintech",
        "industry": "FinTech",
        "items": [
            ("Micro-Invoice Discounting & Supply Chain Finance Marketplace", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-hybrid"],
             "Small vendors wait 90-120 days to get paid by corporate buyers.",
             "A P2P invoice discounting platform verifying corporate purchase orders via TReDS/GST APIs and unlocking early payment.",
             "MSME suppliers, auto ancillary vendors, investors.", "$3.2T invoice discounting market.",
             "Node.js, Hyperledger, GSTN API, React.", "Buyer default risk prediction algorithm.",
             "Transaction commission fee (0.5% to 1.5% of invoice).", "Securing RBI TReDS sandbox approval.",
             "Month 1-2: Smart contract & GST engine. Month 3: Sandbox. Month 4+: Vendor onboarding.", "RBI TReDS Guidelines.", "Factoring Regulation Act."),
            ("Automated Vendor Purchase Order Invoice Factoring Portal", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Textile and garment exporters wait 60 days for overseas buyer invoice clearances.",
             "An online export factoring portal matching verified export invoices with NBFC liquidity providers.",
             "Garment exporters, handicraft manufacturers.", "$2B export factoring market.",
             "Python, TradeFX API, Node.js, PostgreSQL.", "Export buyer creditworthiness ML score.",
             "Factoring fee (1% per funded 30-day invoice).", "Cross-border currency volatility risks.",
             "Month 1-2: Export portal & NBFC integration. Month 3: Exporter pilot. Month 4+: Scaling.", "ECGC Export Insurance Scheme.", "RBI Trade Guidelines."),
            ("Early Payment Cash Discounting SaaS for Suppliers", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Corporates holding surplus cash have no simple mechanism to offer dynamic early payment discounts.",
             "A dynamic discounting SaaS platform allowing suppliers to bid early payment discounts on approved invoices.",
             "Corporate CFOs, procurement teams, suppliers.", "$4B dynamic discounting market.",
             "React, Python, ERP Integration (SAP/Tally API).", "Dynamic APR yield curve optimization for corporate treasury.",
             "SaaS subscription fee (₹15,000/month per corporate).", "ERP integration compatibility.",
             "Month 1-2: Tally/SAP plugin build. Month 3: Corporate pilot. Month 4+: GTM.", "MSME Samadhaan Portal.", "Tally Developer Guide."),
        ]
    },
    {
        "subtopic": "embedded insurance",
        "category_slug": "fintech",
        "industry": "FinTech",
        "items": [
            ("Embedded Micro-Insurance API for Delivery & Gig Workers", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Gig delivery workers lack affordable daily health and accident coverage.",
             "An API SDK embedding single-shift micro-insurance (₹10/day) directly into logistics apps.",
             "Delivery platforms, gig worker unions, InsurTechs.", "$70B embedded insurance market.",
             "Python, RESTful API Gateway, Underwriter Core API.", "Dynamic risk pricing engine calculating shift premiums.",
             "15-20% commission on insurance premiums written.", "Automated instant claim settlement.",
             "Month 1-2: Underwriter API integration. Month 3: Logistics pilot. Month 4+: Expansion.", "IRDAI Regulatory Sandbox.", "Gig Worker Welfare Policy."),
            ("Crop Yield Weather Index Embedded Micro-Insurance Platform", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "Small farmers suffer crop loss from unseasonal rainfall without insurance payouts due to paperwork.",
             "A parametric weather micro-insurance API automatically triggering UPI claims when rainfall drops below threshold.",
             "Agri input apps, FPOs, micro-finance lenders.", "$12B parametric insurance market.",
             "Python, Weather API, Smart Contracts, UPI Stack.", "Satellite rainfall deficit trigger algorithm.",
             "10% platform fee on insurance underwriting volume.", "Hyperlocal weather data API accuracy.",
             "Month 1-2: Parametric smart contract build. Month 3: FPO trial. Month 4+: Scaling.", "PM Fasal Bima Yojana (PMFBY).", "IRDAI Parametric Rules."),
            ("E-Commerce Freight Loss & Transit Embedded Insurance", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "D2C brands suffer damage and loss during courier transit without affordable parcel insurance.",
             "A 1-click checkout insurance widget adding ₹5 per shipment covering transit loss up to ₹5,000.",
             "D2C brands, Shopify merchants, courier aggregators.", "$5B transit insurance market.",
             "Node.js, Shopify App API, Shiprocket API.", "Automated claim approval ML matching courier proof of loss.",
             "₹1.50 retained fee per insured shipment.", "Fraudulent damage claim prevention.",
             "Month 1: Shopify plugin & courier API. Month 2: D2C merchant pilot. Month 3+: Shopify store listing.", "IRDAI Micro-Insurance Guidelines.", "Shopify Developer API."),
        ]
    },

    # ── 6. EDTECH ───────────────────────────────────────────────────────────
    # Subtopics: Adaptive Learning, VR Vocational Labs, Attendance Telemetry, STEM Vernacular
    {
        "subtopic": "adaptive learning",
        "category_slug": "edtech",
        "industry": "EdTech",
        "items": [
            ("AI Adaptive Math & Science Learning Platform for K-12", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-high"],
             "Students learn at different speeds, but classrooms enforce one-size-fits-all teaching.",
             "An adaptive AI engine pinpointing student knowledge gaps and dynamically generating practice questions.",
             "K-12 students, private schools, coaching centers.", "$9B adaptive learning market.",
             "React, Python FastAPI, Knowledge Graph DB, PyTorch IRT.", "Item Response Theory neural net mapping student mastery.",
             "B2C subscription (₹499/student/month) & school licenses.", "Maintaining student engagement retention.",
             "Month 1-2: Adaptive question engine. Month 3: School trial. Month 4+: B2C marketing.", "NEP 2020 Framework.", "DIKSHA National Portal."),
            ("Personalized Adaptive Coding Tutor & Knowledge Graph Engine", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "Beginner coding students get stuck on syntax errors and abandon online courses.",
             "An AI coding workspace analyzing student code execution errors and suggesting targeted mini-lessons.",
             "Computer science students, coding bootcamps.", "$6B online coding education market.",
             "Monaco Editor, Python AST, GPT-4o-mini, Node.js.", "Code AST error pattern classifier generating hint prompts.",
             "Subscription at ₹799/month per student.", "Preventing AI from revealing direct homework answers.",
             "Month 1-2: Monaco IDE & AI hint engine. Month 3: Bootcamp test. Month 4+: Sales.", "Startup India Recognition.", "NEP Tech Education Policy."),
            ("Adaptive Exam Prep & Weakness Analytics Platform", "₹5 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-high"],
             "Competitive exam aspirants (JEE/NEET) waste time practicing topics they have already mastered.",
             "An AI mock test engine analyzing speed and accuracy to force practice on weak sub-topics.",
             "JEE/NEET aspirants, coaching institutes.", "$4B competitive exam market.",
             "React, Python, PostgreSQL, Recharts.", "Exam performance speed-accuracy tradeoff ML model.",
             "Subscription at ₹299/month per student.", "Question bank coverage for all syllabus chapters.",
             "Month 1: Question bank & ML engine. Month 2: Student beta. Month 3+: Coaching partnerships.", "NEP 2020 Assessment Guidelines.", "NTA Exam Syllabus."),
        ]
    },
    {
        "subtopic": "vr vocational labs",
        "category_slug": "edtech",
        "industry": "EdTech",
        "items": [
            ("VR Industrial Electrician & Welding Vocational Simulator", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Vocational ITI institutes lack expensive physical machinery and welding consumables.",
             "An immersive Meta Quest VR simulation lab allowing students to practice electrical wiring and MIG welding safely.",
             "ITIs, polytechnics, manufacturing companies.", "$12B VR training market.",
             "Unity 3D Engine, C#, Meta Quest OpenXR SDK.", "VR haptic feedback scoring evaluating weld seam consistency.",
             "Annual lab license fee (₹1.5 Lakhs/ITI) + VR headset bundle.", "Minimizing VR motion sickness for students.",
             "Month 1-2: Unity VR welding module build. Month 3: ITI college trial. Month 4+: Government tenders.", "PM Kaushal Vikas Yojana.", "NSDC Skill Standards."),
            ("Interactive VR Medical Nursing & Anatomy Simulation Lab", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-hybrid"],
             "Nursing students face limited clinical rotation opportunities to practice emergency patient procedures.",
             "A VR medical lab simulating patient triage, IV injection, and CPR emergency response in 3D.",
             "Nursing colleges, medical schools, hospitals.", "$8B medical VR training market.",
             "Unity 3D, Medical 3D Asset Library, Meta Quest SDK.", "Automated procedural compliance evaluation engine.",
             "Annual college software subscription (₹2.2 Lakhs/college).", "High-polygon 3D medical asset rendering.",
             "Month 1-2: VR nursing scenario build. Month 3: Nursing college trial. Month 4+: Expansion.", "Indian Nursing Council Guidelines.", "NSDC Health Skilling."),
            ("VR Automotive Mechanic Repair Training Module", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Auto mechanic trainees struggle to learn EV battery disassembly without high-voltage shock risks.",
             "A VR workshop simulator teaching EV battery pack disassembly and engine overhaul steps safely.",
             "Auto mechanic training centers, EV OEMs.", "$5B auto VR skilling market.",
             "Unity 3D Engine, OpenXR, C#, WebGL Dashboard.", "Interactive step-by-step disassembly sequence grader.",
             "Hardware/Software training package (₹1.2 Lakhs per lab).", "3D CAD file conversion to VR assets.",
             "Month 1-2: VR EV battery module. Month 3: Auto OEM pilot. Month 4+: Center sales.", "Automotive Skills Development Council.", "ASDTC EV Skilling Report."),
        ]
    },
    {
        "subtopic": "attendance telemetry",
        "category_slug": "edtech",
        "industry": "EdTech",
        "items": [
            ("Automated School RFID & Facial Attendance Telemetry System", "₹5 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Teachers lose 15 minutes per class taking manual roll-call.",
             "A smart gate reader & facial recognition camera gateway logging attendance in 2 seconds and sending WhatsApp alerts.",
             "Private schools, colleges, hostel facilities.", "$7B smart campus market.",
             "Raspberry Pi 4, OpenCV Face Recognition, RFID Reader, Node.js.", "Edge AI facial embedding matching running offline.",
             "School setup fee (₹35,000) + student SaaS fee (₹20/student/month).", "Student DPDP biometric privacy compliance.",
             "Month 1: Gate hardware & face engine. Month 2: School pilot. Month 3+: Sales.", "Digital India School Support.", "DPDP Act Policy."),
            ("Smart Campus Student Attendance & Safety Beacon", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Large university campuses struggle to track student attendance across multiple lecture halls.",
             "Bluetooth Low Energy (BLE) classroom beacons auto-verifying student attendance via mobile app upon entry.",
             "Universities, engineering colleges, coaching hubs.", "$4B campus IoT market.",
             "BLE Beacons, Flutter Student App, Node.js, PostgreSQL.", "Geo-fenced indoor positioning verification algorithm.",
             "Campus beacon kit (₹25,000) + monthly software license.", "Preventing proxy attendance check-ins.",
             "Month 1: BLE beacon app & geo-fence. Month 2: College trial. Month 3+: Campus sales.", "UGC Digital Campus Guidelines.", "NEP Tech Infrastructure."),
            ("Bus Tracking & Student Attendance Telemetry Gateway", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Parents panic when school buses are delayed in traffic without live location updates.",
             "A vehicle GPS + RFID student tap card gateway sending live bus ETA and boarding alerts to parents.",
             "School bus fleet operators, private schools.", "$6B school transport market.",
             "Quectel GPS/GSM Gateway, RFID Reader, Node.js, Firebase.", "Dynamic ETA calculation model adjusting for traffic congestion.",
             "Bus hardware kit (₹8,500/bus) + monthly parent app subscription.", "Cellular dead-zone buffering on rural routes.",
             "Month 1-2: Bus gateway hardware build. Month 3: School fleet pilot. Month 4+: Fleet sales.", "State Motor Vehicles Rules.", "School Transport Guidelines."),
        ]
    },
    {
        "subtopic": "stem vernacular",
        "category_slug": "edtech",
        "industry": "EdTech",
        "items": [
            ("Vernacular STEM Robotics & Electronics Experiment Kit", "₹4 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Tier-2/3 school students lack access to affordable STEM kits with regional language manuals.",
             "A modular DIY electronics & robotics kit accompanied by video tutorials in Hindi, Tamil, and Bengali.",
             "School students (Ages 8-16), STEM labs, Atal Tinkering Labs.", "$14% CAGR educational toys market.",
             "Custom PCB Shield, MicroPython, Arduino IDE, Video Portal.", "Interactive AI chatbot assisting code debug in native language.",
             "Kit sale (₹1,999/kit) + project extension packs.", "Sourcing low-cost reliable sensor components.",
             "Month 1: PCB manufacturing & kit build. Month 2: Localization. Month 3+: E-commerce launch.", "Atal Innovation Mission (ATL).", "NITI Aayog STEM Report."),
            ("Local Language Interactive AI Coding & Science Portal", "₹5 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-high"],
             "Non-English speaking students face language barriers when learning Scratch and Python coding.",
             "A block-based coding portal translated into 8 Indian regional languages with voice-guided coding tutorials.",
             "Regional language schools, government schools.", "$3B vernacular edtech market.",
             "Blockly API, Bhabini Voice API, React, Node.js.", "Vernacular natural language prompt compiler.",
             "School subscription (₹3,000/month per school computer lab).", "Translating technical programming jargon accurately.",
             "Month 1-2: Blockly vernacular translation. Month 3: School trial. Month 4+: School sales.", "NEP Vernacular Education Framework.", "DIKSHA Portal."),
            ("Vernacular Hands-On Maker Lab & Tinkering Curriculum", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Rural schools lack trained science teachers to conduct practical physics and chemistry experiments.",
             "A portable maker lab trunk with 50+ curriculum-aligned science experiments and vernacular video guides.",
             "Rural private schools, NGO learning centers.", "$4B hands-on learning market.",
             "3D Printed Lab Tools, Micro-Sensors, Vernacular App.", "Interactive experiment result verification algorithm.",
             "Maker lab trunk sale (₹28,000/trunk per school).", "Chemical reagent safety packaging.",
             "Month 1-2: Trunk lab design & curriculum. Month 3: Rural school test. Month 4+: Sales.", "Atal Innovation Mission (AIM).", "NCERT Science Syllabus."),
        ]
    },

    # ── 7. CLEAN ENERGY ─────────────────────────────────────────────────────
    # Subtopics: Solar Microgrids, Biomass Briquettes, Second-Life Battery, Micro-Wind
    {
        "subtopic": "solar microgrids",
        "category_slug": "renewable-energy",
        "industry": "Clean Energy",
        "items": [
            ("Village Solar Microgrid Power Distribution & Smart Metering", "₹9 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Off-grid rural hamlets suffer blackouts, while diesel generators cause high operating costs.",
             "A 10kW rooftop solar microgrid equipped with smart prepaid meters supplying electricity to 30 village homes.",
             "Rural panchayats, off-grid resorts, telecom towers.", "$22B solar microgrid market.",
             "10kW Solar Array, MPPT Controller, LiFePO4 Battery, Smart Meter.", "AI load shedding algorithms prioritizing essential loads.",
             "Prepaid electricity tariff sales (₹8 - ₹12 per kWh).", "Battery bank replacement capital costs.",
             "Month 1-2: Microgrid design & solar install. Month 3: Village commissioning. Month 4+: Franchise.", "PM-KUSUM Scheme.", "MNRE Off-Grid Solar Policy."),
            ("Commercial Rooftop Solar Microgrid Controller", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Commercial buildings struggle to optimize power switching between grid, solar, and diesel generators.",
             "An automatic smart transfer switch controller optimizing solar consumption and reducing diesel usage.",
             "Commercial buildings, hospitals, IT parks.", "$14B commercial solar market.",
             "Industrial PLC, MODBUS Meters, Python, React Dashboard.", "Solar generation forecasting neural net using cloud cover API.",
             "Controller hardware sale (₹1.2 Lakhs) + monthly SaaS.", "High-voltage relay arc suppression.",
             "Month 1-2: Transfer switch PLC build. Month 3: Building trial. Month 4+: B2B sales.", "MNRE Rooftop Solar Scheme.", "CEA Grid Interconnection Rules."),
            ("Pay-As-You-Go Agricultural Solar Microgrid Pump", "₹7 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Small farmers cannot afford ₹2.5 Lakhs upfront to buy individual solar water pumps.",
             "A shared community solar pump microgrid where farmers pay for irrigation water per hour via mobile wallet.",
             "Smallholder farmers, sugarcane cooperatives.", "$9B agri solar pump market.",
             "5HP Solar Pump, IoT Motor Controller, Mobile Wallet API.", "Water volume flow rate metering algorithm.",
             "Hourly water rental fee (₹60/hour of pumping).", "Preventing water theft and hose pipe damage.",
             "Month 1-2: Solar pump & IoT wallet setup. Month 3: Village trial. Month 4+: Franchise model.", "PM-KUSUM Component B Subsidy.", "NABARD Agri Infrastructure Fund."),
        ]
    },
    {
        "subtopic": "biomass briquettes",
        "category_slug": "renewable-energy",
        "industry": "Clean Energy",
        "items": [
            ("Biomass Pellet & Briquette Manufacturing Unit", "₹8 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Stubble burning of agricultural residue causes severe air pollution, while power plants need green fuel.",
             "A compact hydraulic biomass briquetting plant compressing agricultural stubble into eco-friendly fuel pellets.",
             "Thermal power plants, industrial boiler operators, brick kilns.", "100M ton mandated biomass market.",
             "Biomass Shredder, Rotary Dryer, Ring Die Pellet Mill.", "Moisture optimization sensors regulating binder addition.",
             "Bulk sale of pellets to thermal plants (₹5,500 - ₹7,200/ton).", "Seasonal availability of crop residue.",
             "Month 1: Site selection & machinery order. Month 2: Installation. Month 3+: Supply execution.", "MNRE Biomass Programme.", "Ministry of Power SAMARTH Policy."),
            ("Paddy Straw Stubble High-Calorific Briquette Press", "₹9 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-non-ai"],
             "Paddy straw has low bulk density and high silica content, making standard briquetting difficult.",
             "A heavy-duty 75HP mechanical piston press specially engineered to compact high-silica paddy straw into industrial briquettes.",
             "Power plants, sugar mill boilers, chemical plants.", "$8B bioenergy market.",
             "75HP Mechanical Piston Press, Heavy Shredder, Rotary Dryer.", "High-friction compaction heat management algorithm.",
             "Briquette bulk sales at ₹6,000/ton.", "Piston sleeve wear from abrasive silica.",
             "Month 1-2: Piston press procurement. Month 3: Stubble pressing trial. Month 4+: Power plant contracts.", "SAMARTH Mission Co-firing.", "MNRE Bioenergy Scheme."),
            ("Organic Waste Wood Pellet Processing Plant", "₹7 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Timber mills and carpentry workshops generate piles of saw-dust that pose fire hazards.",
             "A 300kg/hr sawdust pelletizing line producing clean wood pellets for commercial bakeries and home stoves.",
             "Commercial bakeries, hotel kitchens, pellet stove owners.", "$6B wood pellet market.",
             "Hammer Mill, Flat Die Pellet Machine, Bagging Scale.", "Pellet density & durability testing algorithm.",
             "Wood pellet sales (₹9,000/ton bagged).", "Sawdust moisture consistency before pressing.",
             "Month 1: Machinery setup. Month 2: Sawdust supply agreements. Month 3+: Bakery distribution.", "KVIC PMEGP Loan Scheme.", "MNRE Bioenergy Guidelines."),
        ]
    },
    {
        "subtopic": "second-life battery",
        "category_slug": "renewable-energy",
        "industry": "Clean Energy",
        "items": [
            ("Second-Life EV Lithium Battery Pack Refurbishing Facility", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-hybrid"],
             "Retired EV batteries retain 70-80% capacity but are discarded, creating toxic electronic waste.",
             "A diagnostic facility sorting retired 2W/3W EV lithium cells and repackaging them into stationary solar storage units.",
             "Solar installers, telecom backup providers, UPS buyers.", "$15B second-life battery market.",
             "Battery Impedance Tester, Automated Cell Sorter, Smart BMS.", "State of Health (SOH) impedance spectroscopy model.",
             "Refurbished pack sales (₹6,000/kWh - 50% cheaper than new).", "Safe thermal management during cell sorting.",
             "Month 1-2: Diagnostic bench setup. Month 3: Storage pack build. Month 4+: Commercial sales.", "Battery Waste Rules 2022.", "BIS AIS 156 Battery Standard."),
            ("Retired EV Battery Solar Energy Storage System (BESS)", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Commercial solar systems require expensive lithium storage packs, inflating payback periods.",
             "A 5kWh solar energy storage cabinet built from second-life EV battery modules with active cell balancing.",
             "Small shops, petrol pumps, off-grid homes.", "$10B BESS storage market.",
             "Second-Life LiFePO4 Modules, 5kW Hybrid Inverter, Active BMS.", "Cell voltage balancing & thermal runaway prevention algorithm.",
             "Cabinet unit sale (₹75,000 per 5kWh cabinet).", "Matching cells with identical internal resistance.",
             "Month 1-2: Cabinet build & BMS tuning. Month 3: Shop pilot. Month 4+: Solar installer sales.", "MNRE Energy Storage Scheme.", "CEA Safety Regulations."),
            ("Lithium Battery Cell Sorting & Health Diagnostic Bench", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Battery recyclers lack automated tools to sort thousands of mixed 18650/21700 lithium cells quickly.",
             "A robotic 4-channel automated cell tester measuring capacity, internal resistance, and voltage in 30 seconds.",
             "Battery refurbishers, e-waste recyclers, EV service centers.", "$4B battery diagnostic market.",
             "4-Channel Electronic Load, Pneumatic Gripper, Python, React.", "Automated cell grading & binning algorithm.",
             "Diagnostic bench sale (₹1.8 Lakhs) to battery recyclers.", "High-current contact resistance calibration.",
             "Month 1-2: Robotic tester bench build. Month 3: Recycler test. Month 4+: Machine sales.", "EPR Certificate Trading Scheme.", "MoEFCC E-Waste Rules."),
        ]
    },
    {
        "subtopic": "micro-wind",
        "category_slug": "renewable-energy",
        "industry": "Clean Energy",
        "items": [
            ("Highway Micro-Wind Turbine Generator for Street Lighting", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-non-ai"],
             "National highways consume vast grid power for continuous nocturnal street lighting.",
             "Vertical-axis micro-wind turbines mounted on highway medians generating power from vehicle air draft.",
             "National Highway Authority (NHAI), toll plaza operators.", "$12% CAGR micro-wind market.",
             "Vertical Axis Wind Turbine (VAWT), Magnet Generator, LiFePO4.", "Rotor blade aerodynamic fluid dynamics optimization.",
             "Turbine hardware sale (₹45,000/pole unit).", "Vibration damping against high vehicle speeds.",
             "Month 1-2: VAWT rotor fabrication. Month 3: Highway median demo. Month 4+: NHAI tenders.", "MNRE Small Wind Programme.", "NHAI Green Highway Guidelines."),
            ("Coastal Rooftop Hybrid Micro-Wind & Solar Generator", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-non-ai"],
             "Coastal homes experience high night wind speeds but lose power when solar generation drops after sunset.",
             "A hybrid 1kW rooftop vertical wind turbine + 1kW solar panel system delivering 24/7 renewable power.",
             "Coastal resorts, island homes, marine research stations.", "$7B hybrid renewable market.",
             "1kW VAWT Turbine, 1kW Solar Array, Hybrid Inverter, Battery.", "Wind/solar power blending MPPT algorithm.",
             "Hybrid system sale (₹1.4 Lakhs complete kit).", "Corrosion resistance against salty coastal air.",
             "Month 1-2: Marine-grade VAWT assembly. Month 3: Coastal resort trial. Month 4+: Regional sales.", "MNRE Off-Grid Scheme.", "NIWE Wind Potential Map."),
            ("Vertical Axis Micro-Wind Turbine for Telemetry Towers", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Remote cellular towers in windy hill stations spend ₹40,000/month on diesel generator backup fuel.",
             "A compact 500W omnidirectional micro-wind turbine mounted on telecom tower frames.",
             "Telecom tower companies (Indus Towers, ATC), weather stations.", "$5B telecom green energy market.",
             "500W VAWT Turbine, Direct Drive Generator, Charge Controller.", "Omnidirectional wind capture aerodynamic blade profile.",
             "Turbine unit sale (₹35,000/unit) to tower companies.", "Wind vibration transmission to tower antenna.",
             "Month 1: Turbine build & tower mount test. Month 2: Telecom tower pilot. Month 3+: Tower sales.", "TRAI Green Telecom Guidelines.", "MNRE Small Wind Policy."),
        ]
    },

    # ── 8. CONSTRUCTION & INFRASTRUCTURE ───────────────────────────────────
    # Subtopics: Modular Prefab, Drone Site Safety, Eco Interlocking Bricks, Concrete Sensors
    {
        "subtopic": "modular prefab",
        "category_slug": "construction-tech",
        "industry": "Construction & Infrastructure",
        "items": [
            ("Lightweight Modular Prefab Steel House Manufacturing", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-non-ai"],
             "Traditional brick construction takes 8-12 months and suffers heavy labor cost overruns.",
             "Factory-manufactured Light Gauge Steel Frame (LGSF) modular wall panels assembled on site in 15 days.",
             "Resort developers, site office contractors, rooftop extension builders.", "$130B modular construction market.",
             "LGSF Roll Former, CAD Frame Builder, PUF Wall Panels.", "Automated CAD-to-CAM nesting algorithms minimizing steel cut waste.",
             "Turnkey construction pricing at ₹1,200 - ₹1,800/sq.ft.", "Seismic & wind load structural certification.",
             "Month 1-2: LGSF roll former procurement. Month 3: Sample site office build. Month 4+: B2B sales.", "PMAY Light House Projects.", "IS 800 Steel Code."),
            ("Prefabricated Bathroom & Kitchen Pod Assembly Unit", "₹9 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-non-ai"],
             "Multi-story hotel and apartment projects experience construction bottlenecks in manual bathroom plumbing.",
             "Fully fitted off-site prefabricated bathroom pods including tiles, plumbing, and fixtures dropped in via crane.",
             "Hotel chains, high-rise residential developers, hospital builders.", "$18B prefab pod market.",
             "Steel Chassis, Fiber Cement Board, Pre-Plumbed Manifold.", "Standardized modular dimension parametric CAD model.",
             "Per-pod sale price (₹65,000 to ₹1.2 Lakhs per bathroom pod).", "Transportation clearance dimensions for truck haulage.",
             "Month 1-2: Pod jig setup & plumbing manifold. Month 3: Hotel builder pilot. Month 4+: Developer sales.", "BMTPC Innovation Scheme.", "National Building Code."),
            ("Modular Fast-Deploy Emergency Shelter System", "₹7 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Disaster relief operations struggle to erect sturdy waterproof housing within 48 hours of flooding.",
             "Flat-pack snap-together insulated polypropylene wall panels assembled without tools in 45 minutes.",
             "Disaster management authorities (NDRF), military, NGOs.", "$6B emergency housing market.",
             "Honeycomb Polypropylene Panels, Aluminum Connectors.", "Modular snap-latch joint stress distribution modeling.",
             "Flat-pack shelter sale (₹35,000 per 4-person shelter unit).", "Extreme wind uplift anchoring.",
             "Month 1-2: Flat-pack mold tooling & snap joint test. Month 3: NDRF demo. Month 4+: Government tenders.", "NDRF Emergency Procurement.", "UNHCR Shelter Standards."),
        ]
    },
    {
        "subtopic": "drone site safety",
        "category_slug": "construction-tech",
        "industry": "Construction & Infrastructure",
        "items": [
            ("Construction Site Safety Inspection Drone & AI Helmet Detector", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "Construction contractors face severe legal liabilities due to unmonitored PPE safety violations.",
             "An autonomous site drone streaming video to an AI model flagging unhelmeted workers and fall hazards.",
             "Real estate developers, infrastructure contractors, safety auditors.", "19% CAGR construction drone market.",
             "PX4 Quadcopter, 4K Camera, Jetson Orin Edge Gateway, YOLOv8.", "Real-time computer vision PPE detector identifying hardhats at 30 FPS.",
             "Monthly safety monitoring fee (₹25,000/month per site).", "Navigating around crane towers & scaffolding.",
             "Month 1: Safety AI model training. Month 2: Drone site pilot. Month 3+: Developer contracts.", "DGCA DigitalSky Compliance.", "DGFASLI Safety Rules."),
            ("Drone Surveying 3D Volumetric Stockpile Mapping Platform", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "Mining and earthwork contractors struggle to measure sand and gravel stockpile volumes accurately.",
             "Autonomous surveying drones generating 3D digital elevation models (DEM) and volumetric cut/fill metrics.",
             "Mining companies, quarry operators, highway builders.", "$8B drone surveying market.",
             "RTK Quadcopter, Photogrammetry Software, Python, WebGL.", "Automated 3D point cloud volumetric calculation algorithm.",
             "Per-survey reporting charge (₹15,000 per quarry survey).", "RTK GPS accuracy calibration in deep quarries.",
             "Month 1-2: Photogrammetry pipeline & RTK drone setup. Month 3: Quarry pilot. Month 4+: Sales.", "DGCA Drone Regulations.", "Indian Bureau of Mines Rules."),
            ("Structural Inspection & Facade Defect Drone Scanner", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-high"],
             "High-rise building facade inspections require risky manual rope access or scaffolding.",
             "A close-range obstacle-avoidance drone taking thermal & optical high-res photos to detect concrete facade cracks.",
             "Building audit agencies, municipal corporations, estate managers.", "$5B facade inspection market.",
             "LiDAR Shielded Quadcopter, Thermal Camera, OpenCV, PyTorch.", "AI crack width classification neural network measuring 0.5mm defects.",
             "Building facade inspection fee (₹45,000 per high-rise audit).", "Wind turbulence near glass high-rise walls.",
             "Month 1-2: Shielded drone & thermal camera. Month 3: High-rise audit trial. Month 4+: Audit sales.", "National Building Code 2016.", "DGCA Commercial Drone Rules."),
        ]
    },
    {
        "subtopic": "eco interlocking bricks",
        "category_slug": "construction-tech",
        "industry": "Construction & Infrastructure",
        "items": [
            ("Recycled Plastic & Fly-Ash Interlocking Eco-Bricks", "₹5 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Traditional clay brick kilns cause carbon emissions, while plastic waste clogs landfills.",
             "A compression moulding process combining shredded waste plastic with fly-ash to manufacture mortar-less interlocking bricks.",
             "Real estate developers, municipal park builders, wall contractors.", "12% CAGR green building materials.",
             "Plastic Shredder, Heated Mixer, 50-Ton Hydraulic Press.", "Automated material ratio calculation ensuring >15 MPa strength.",
             "Per brick sale (₹9 to ₹14 per brick) offering 30% labor savings.", "Fire retardancy rating compliance (UL 94-V0).",
             "Month 1: Hydraulic press procurement. Month 2: Compression test. Month 3+: Sales.", "Swachh Bharat Innovation Fund.", "IS 1077 Brick Standard."),
            ("Compressed Stabilized Earth Interlocking Brick Machine", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Rural housing projects incur high transportation costs hauling clay bricks from distant kilns.",
             "A mobile hydraulic press producing high-strength interlocking earth blocks directly from local excavated soil.",
             "Low-cost housing contractors, rural panchayats, eco-resorts.", "$7B sustainable masonry market.",
             "Mobile Trailer Press, Diesel Engine, Hydraulic Cylinder, Molds.", "Soil clay/sand ratio field moisture optimization algorithm.",
             "Machine sale (₹3.2 Lakhs) or rental per 1,000 blocks produced.", "Soil clay percentage testing on-site.",
             "Month 1: Mobile press fabrication. Month 2: Rural housing trial. Month 3+: Contractor sales.", "PMAY Rural Housing Scheme.", "BMTPC Earth Block Standard."),
            ("Industrial Slag & Rice Husk Sustainable Building Bricks", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-non-ai"],
             "Steel plants generate toxic blast furnace slag waste that accumulates in industrial dumps.",
             "A geopolymer brick manufacturing line utilizing granulated blast furnace slag and rice husk ash.",
             "Industrial builders, infrastructure contractors, boundary wall developers.", "$9B eco-masonry market.",
             "Pan Mixer, Vibrating Block Machine, Curing Chamber.", "Geopolymer alkaline activator ratio optimization algorithm.",
             "Eco-block sale price (₹18 per 8-inch block).", "Alkaline activator handling safety.",
             "Month 1-2: Block machine setup & geopolymer formula. Month 3: Lab strength test. Month 4+: Sales.", "MoEFCC Industrial Waste Utilisation Rules.", "IS 2185 Concrete Block Code."),
        ]
    },
    {
        "subtopic": "concrete sensors",
        "category_slug": "construction-tech",
        "industry": "Construction & Infrastructure",
        "items": [
            ("Embedded IoT Wireless Concrete Maturity & Cure Sensor", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Construction teams wait 28 conservative days for concrete cylinder break tests before removing formwork.",
             "A sacrificial wireless cable sensor embedded directly into poured concrete transmitting temperature and strength data.",
             "High-rise builders, bridge contractors, ready-mix concrete suppliers.", "$1.6B smart concrete market.",
             "Sacrificial Thermistor Probe, BLE Pod, Android App, ASTM C1074.", "Concrete mix maturity curve forecasting predicting formwork removal hour.",
             "Disposable sensor cable sale (₹450/sensor) + app analytics fee.", "BLE pod survival during heavy concrete pouring.",
             "Month 1: Sensor pod fabrication. Month 2: Lab cylinder validation. Month 3+: Contractor sales.", "BMTPC Innovation Grant.", "ASTM C1074 Maturity Standard."),
            ("Ultrasonic Concrete Structural Integrity Test Probe", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Bridge pillars and dam walls develop internal void pockets that are invisible from the surface.",
             "A portable non-destructive ultrasonic pulse velocity (UPV) tester mapping internal concrete voids.",
             "Bridge inspection engineers, structural auditors, NDT labs.", "$4B NDT concrete market.",
             "Piezoelectric Ultrasonic Transducers, High-Speed ADC, STM32, React.", "Ultrasonic wave velocity tomography model creating 2D void cross-sections.",
             "NDT tester hardware sale (₹85,000) + audit reporting SaaS.", "Couplant gel application interface consistency.",
             "Month 1-2: UPV circuit & transducer bench. Month 3: NDT lab calibration. Month 4+: Audit sales.", "IS 13311 Non-Destructive Testing Code.", "IRC Bridge Inspection Code."),
            ("Concrete Rebar Corrosion Monitoring Sensor Node", "₹7 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Coastal concrete bridges fail prematurely due to unmonitored saltwater rebar rust corrosion.",
             "An embedded half-cell potential sensor probe monitoring rebar corrosion current continuously.",
             "Port authorities, coastal highway departments, marine contractors.", "$3B rebar protection market.",
             "Reference Electrode Probe, Low-Power MCU, NB-IoT, Web Dashboard.", "Corrosion rate electro-chemical regression neural net.",
             "Embedded probe price (₹1,200/probe) + marine monitoring SaaS.", "Sensor reference electrode 10-year lifespan.",
             "Month 1-2: Corrosion probe build & saline tank test. Month 3: Port bridge trial. Month 4+: Sales.", "National Highway Authority Guidelines.", "ASTM C876 Rebar Corrosion Standard."),
        ]
    },

    # ── 9. FOOD PROCESSING ──────────────────────────────────────────────────
    # Subtopics: Fruit Powder, Cold-Pressed Oil, Retort Packaging, Millet Snacks
    {
        "subtopic": "fruit powder",
        "category_slug": "food-processing",
        "industry": "Food Processing",
        "items": [
            ("Dehydrated Fruit & Vegetable Powder Processing Unit", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Perishable crops like onion, tomato, and mango face severe post-harvest price crashes.",
             "A micro food processing facility utilizing heat pump dryers to convert surplus produce into shelf-stable powders.",
             "FMCG food brands, cloud kitchens, hotel chains, spice blenders.", "$115B dehydrated food market.",
             "Heat Pump Dehydrator, Commercial Pulverizer, Vacuum Sealer.", "Moisture grading computer vision & temperature profile automation.",
             "B2B sales of dried powders (₹350 - ₹900/kg) + contract processing.", "FSSAI compliance licensing & flavor preservation.",
             "Month 1: Facility layout & FSSAI setup. Month 2: Equipment install. Month 3+: B2B supply.", "PMFME Scheme 35% Subsidy.", "FSSAI Food Safety Standards."),
            ("Spray-Dried Mango & Papaya Powder Processing Plant", "₹9 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-non-ai"],
             "Fruit juice manufacturers import expensive spray-dried fruit powders for beverage bases.",
             "A micro spray dryer converting fresh mango and papaya pulp into 100% soluble fruit powders.",
             "Beverage manufacturers, confectionery brands, ice cream makers.", "$8B spray-dried food market.",
             "Micro Spray Dryer Tower, Atomizer Nozzle, Cyclonic Separator.", "Nozzle atomization particle size optimization algorithm.",
             "B2B fruit powder sales (₹650/kg).", "Preventing powder sticking on spray tower walls.",
             "Month 1-2: Spray dryer tower setup. Month 3: Trial powder batches. Month 4+: B2B sales.", "APEDA Export Grant.", "FSSAI Beverage Standards."),
            ("Organic Tomato & Onion Seasoning Powder Mill", "₹5 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Snack food manufacturers suffer seasonal tomato and onion price spikes during raw sourcing.",
             "A specialized low-temperature vacuum tray drying mill processing fresh tomatoes into seasoning grade powders.",
             "Snack seasoning blenders, noodle makers, restaurant chains.", "$6B seasoning powder market.",
             "Vacuum Tray Dryer, Pin Mill Pulverizer, Mesh Sieve, Sealer.", "Vacuum pressure vs drying time optimization algorithm.",
             "Bulk seasoning powder sales (₹420/kg).", "Hygroscopic moisture caking prevention in storage.",
             "Month 1: Vacuum dryer install & FSSAI. Month 2: Trial milling. Month 3+: B2B sales.", "PMFME Micro Scheme.", "FSSAI Spices Regulations."),
        ]
    },
    {
        "subtopic": "cold-pressed oil",
        "category_slug": "food-processing",
        "industry": "Food Processing",
        "items": [
            ("Automatic Cold-Pressed Mustard & Sesame Oil Extraction Unit", "₹5 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Consumers shift away from chemically refined oils toward unrefined cold-pressed oils.",
             "A hygienic micro-extraction unit using wooden ghani (Kacchi Ghani) screw presses to produce pure cold-pressed oil.",
             "Health-conscious households, organic grocery stores, D2C brands.", "18% CAGR Indian cold-pressed oil market.",
             "Wooden Ghani Oil Expeller, Oil Filter Press, Stainless Tanks.", "IoT temperature monitoring ensuring extraction temperature stays <45°C.",
             "Direct retail & wholesale sale of bottled oil (₹320 - ₹600/liter).", "Sourcing high-quality unadulterated oilseeds.",
             "Month 1: Ghani machine & FSSAI license. Month 2: Trial pressings. Month 3+: Local shop distribution.", "PMFME Scheme 35% Subsidy.", "FSSAI Edible Oil Standards."),
            ("Virgin Coconut Oil Micro-Processing Plant", "₹7 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Commercial coconut oil processed with heat loses natural lauric acid and antioxidant properties.",
             "A centrifuge micro-processing plant extracting 100% pure Virgin Coconut Oil (VCO) from fresh coconut milk without heat.",
             "Cosmetics brands, premium D2C food brands, Ayurvedic pharmacies.", "$5B global VCO market.",
             "Coconut De-husker, Milk Extractor, Tubular Centrifuge, Filter.", "Centrifugal speed separation optimization algorithm.",
             "Bottled VCO sales (₹750/liter retail).", "Managing perishable coconut water by-products.",
             "Month 1-2: Centrifuge machinery setup & FSSAI. Month 3: Trial run. Month 4+: D2C sales.", "Coconut Development Board Grant.", "FSSAI VCO Standards."),
            ("Wood-Pressed Groundnut & Sunflower Oil Extraction Mill", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Local grocery buyers seek fresh groundnut oil processed transparently in front of them.",
             "A store-front micro-milling setup operating low-speed wooden press expellers for fresh groundnut oil.",
             "Local neighborhood retail buyers, organic stores.", "$4B wood-pressed oil market.",
             "Dual Wooden Expeller Ghani, Stainless Filter, Glass Bottle Sealer.", "Moisture content seed conditioning algorithm.",
             "Store-front retail sales + oil cake animal feed by-product sales.", "Managing oil sedimentation settling time.",
             "Month 1: Store-front setup & FSSAI. Month 2: Ghani installation. Month 3+: Retail sales.", "KVIC PMEGP Loan.", "FSSAI Retail Safety Rules."),
        ]
    },
    {
        "subtopic": "retort packaging",
        "category_slug": "food-processing",
        "industry": "Food Processing",
        "items": [
            ("Ready-to-Eat Retort Pouch Food Packaging Facility", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-non-ai"],
             "Regional food brands cannot export traditional curries without artificial preservatives due to 3-day shelf life.",
             "A commercial retort pouch sterilization unit giving ethnic curries a 12-month ambient shelf life.",
             "Cloud kitchens, ethnic food exporters, defense suppliers.", "$4.5B retort packaging market.",
             "Steam-Air Retort Autoclave, Impulse Sealer, Temp Recorder.", "Automated Fo thermal lethality value calculator eliminating spores.",
             "Contract packaging service fee (₹12 - ₹25/pouch) + branded sales.", "Pouch seal integrity verification to prevent leaks.",
             "Month 1-2: Retort sterilizer procurement & FSSAI. Month 3: Thermal validation. Month 4+: Packaging contracts.", "PMFME Scheme.", "US FDA LACF Guidelines."),
            ("Retort Sterilization Unit for Ethnic Soups & Curries", "₹9 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-non-ai"],
             "Restaurant chains lose money discarding unsold perishable curry batches at closing time.",
             "A centralized batch retort processing hub converting unsold restaurant curries into packaged retail pouches.",
             "Restaurant chains, catering companies, cloud kitchens.", "$6B ready-to-eat meal market.",
             "Batch Retort Kettle, Multi-Layer Foil Pouches, Sealer.", "Curry viscosity heat penetration rate calculation.",
             "Processing fee per batch + revenue share on retail sales.", "Preserving delicate spice aromas during high-heat retorting.",
             "Month 1-2: Retort kettle install & FSSAI. Month 3: Restaurant trial. Month 4+: Hub operations.", "APEDA Export Infrastructure Grant.", "FSSAI RTE Food Code."),
            ("Vacuum Sealed Shelf-Stable Retort Meal Processing Unit", "₹7 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Outdoor campers and emergency relief teams require high-calorie non-refrigerated meals.",
             "A micro facility producing self-heating retort meal kits for emergency response and trekking.",
             "Trekking groups, disaster relief agencies, military canteens.", "$3B MRE (Meals Ready to Eat) market.",
             "Vacuum Chamber Packaging Machine, Retort Cooker, Exothermic Heating Pad.", "Self-heating chemical reaction water ratio optimization.",
             "Unit price per self-heating meal kit (₹180/kit).", "Exothermic heating pouch transport safety.",
             "Month 1: Vacuum sealer & retort setup. Month 2: Meal kit trial. Month 3+: Disaster agency sales.", "National Disaster Management Fund.", "FSSAI Packaging Rules."),
        ]
    },
    {
        "subtopic": "millet snacks",
        "category_slug": "food-processing",
        "industry": "Food Processing",
        "items": [
            ("Multi-Millet Extruded Puff & Healthy Snack Manufacturing", "₹7 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Junk food snacks cause health issues, while healthy millet alternatives are expensive or unpalatable.",
             "A twin-screw extrusion plant processing ragi and jowar millets into roasted, seasoned healthy puffs.",
             "School canteens, supermarket chains, D2C health brands.", "UN International Year of Millets market expansion.",
             "Twin-Screw Extruder, Rotary Flavoring Drum, Belt Dryer.", "AI sensory flavor optimization matching regional preferences.",
             "Branded snack packet sales (₹20 & ₹50 price points).", "Managing millet flour expansion ratio during extrusion.",
             "Month 1: Extruder install & recipe formulation. Month 2: FSSAI. Month 3+: Retail distribution.", "PMFME Scheme for Millets.", "IIMR Millet Processing Guide."),
            ("Roasted Ragi & Jowar Superfood Bakery Plant", "₹6 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-non-ai"],
             "Diabetic consumers seek zero-maida, gluten-free cookies and crackers for daily tea-time snacking.",
             "A micro bakery manufacturing 100% gluten-free ragi, bajra, and jowar cookies and crispbreads.",
             "Diabetic patients, organic food stores, D2C health brands.", "$5B gluten-free bakery market.",
             "Rotary Rack Oven, Dough Mixer, Cookie Dropping Machine.", "Gluten-free dough binder moisture optimization formula.",
             "Retail cookie box sales (₹150/box) + white-labeling.", "Gluten cross-contamination prevention.",
             "Month 1: Bakery oven setup & FSSAI. Month 2: Recipe trials. Month 3+: Organic store sales.", "KVIC PMEGP Loan.", "FSSAI Gluten-Free Standards."),
            ("Instant Millet Breakfast Cereal Processing Line", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-non-ai"],
             "Urban consumers want fast breakfast options but avoid sugary wheat/corn flake cereals.",
             "A flaking & roasting line making instant millet flakes (Ragi & Bajra Flakes) eaten with milk.",
             "Urban households, health food buyers, hotel breakfast buffets.", "$7B breakfast cereal market.",
             "Grain Steamer, Flaking Roller Mill, Rotary Roaster.", "Millet gelatinization temperature control algorithm.",
             "Cereal pouch sales (₹220 per 400g pack).", "Maintaining crispness in humid tropical weather.",
             "Month 1-2: Flaking mill setup & FSSAI. Month 3: Retail trial. Month 4+: Supermarket listing.", "PMFME Scheme.", "IIMR Hyderabad Guidelines."),
        ]
    },

    # ── 10. ROBOTICS & AUTOMATION ───────────────────────────────────────────
    # Subtopics: Spraying Drones, Pipe Inspection Crawlers, Mobile Robots, Robotic Welding
    {
        "subtopic": "spraying drones",
        "category_slug": "robotics",
        "industry": "Robotics & Automation",
        "items": [
            ("Agricultural Spraying & Crop Health Drone Startup", "₹7 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-hybrid"],
             "Manual pesticide spraying is labor-intensive and hazardous to farm workers.",
             "DGCA-compliant hexacopter drones equipped with ultra-low volume nozzles for precision spraying.",
             "FPOs, sugarcane & cotton farmers, agri service providers.", "50-100% government drone subsidy market.",
             "PX4 Autopilot, Carbon Airframe, 10L Spray Tank, Raspberry Pi.", "NDVI weed map processing for spot spraying.",
             "Per-acre custom spraying service fee (₹450 - ₹650/acre).", "Battery cycle life limitation & DGCA pilot certification.",
             "Month 1: Drone assembly & pilot license. Month 2: FPO demos. Month 3+: Spraying operations.", "SMAM Drone Subsidy.", "DGCA DigitalSky Portal."),
            ("Ultra-Low Volume Orchard Pesticide Spraying Drone", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Tall fruit orchards (mango, apple) cannot be sprayed effectively with ground backpacks.",
             "A heavy-lift 16L spraying drone with downward air-wash propellers penetrating dense tree canopies.",
             "Mango orchard owners, apple growers, citrus farms.", "$6B orchard automation market.",
             "PX4 Flight Controller, 16L Tank, Centrifugal Nozzles, Radar.", "Terrain-following radar maintaining fixed height above canopy.",
             "Custom orchard spraying service (₹900/acre).", "Navigating steep hillside orchard terrain.",
             "Month 1-2: Heavy-lift drone build & radar integration. Month 3: Orchard trial. Month 4+: Service sales.", "AIF Agri Infrastructure Fund.", "DGCA Commercial Drone Rules."),
            ("Autonomous Liquid Fertilizer Spraying Hexacopter", "₹9 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Liquid nano-urea fertilizer application requires precise drop-size spraying to prevent leaf burn.",
             "An autonomous hexacopter equipped with electrostatic spraying nozzles ensuring 100% leaf underside coverage.",
             "Fertilizer companies (IFFCO), large farms, FPOs.", "$8B liquid fertilizer market.",
             "ArduPilot, Electrostatic Nozzles, 12L Tank, 4G Telemetry.", "Electrostatic droplet charge optimization algorithm.",
             "Custom spraying contracts with fertilizer distributors.", "Electrostatic nozzle clogging maintenance.",
             "Month 1-2: Hexacopter & electrostatic setup. Month 3: Field test. Month 4+: Corporate contracts.", "SMAM Scheme.", "ICAR Drone Spraying Guidelines."),
        ]
    },
    {
        "subtopic": "pipe inspection crawlers",
        "category_slug": "robotics",
        "industry": "Robotics & Automation",
        "items": [
            ("Robotic Pipe Inspection & Pipeline Leak Detection System", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-high"],
             "Municipalities and chemical plants suffer major water/fuel loss due to undetected internal pipe cracks.",
             "A tethered magnetic crawler robot equipped with ultrasonic thickness gauges inspecting pipe interiors.",
             "Municipal water boards, refineries, chemical plants.", "$2.4B pipeline inspection market.",
             "ROS2, Magnetic Track Drive, Ultrasonic Transducer, Jetson Nano.", "Real-time computer vision detection of corrosion pitting.",
             "Inspection service contracts (₹15,000 to ₹40,000/km scanned).", "IP68 waterproofing & navigating tight 90° pipe elbows.",
             "Month 1-2: Crawler build & waterproofing. Month 3: Lab testing. Month 4-6: Utility trials.", "AMRUT 2.0 Water Grant.", "NACE Pipeline Standards."),
            ("Sewer Line Magnetic Crawler Inspection Robot", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-high"],
             "Manual sewer cleaning is illegal and dangerous for municipal sanitation workers.",
             "A waterproof sewer inspection crawler with 360° pan-tilt camera detecting blockages and structural collapse.",
             "Municipal corporations, urban local bodies, sanitation contractors.", "$4B municipal sewer robotics market.",
             "IP68 Chassis, Pan-Tilt Camera, ROS2, Kevlar Tether, OpenCV.", "AI sludge accumulation and structural crack classifier.",
             "Crawler hardware sale (₹4.5 Lakhs) or municipal service fee.", "Methane gas explosion hazard protection (ATEX rating).",
             "Month 1-2: IP68 sewer crawler build. Month 3: Municipal sewer test. Month 4+: Government tenders.", "Swachh Bharat Sanitation Grant.", "Safaimitra Suraksha Challenge."),
            ("Industrial Chimney & Tank Ultrasonic Inspection Crawler", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-high"],
             "Refinery storage tanks and power plant chimneys require hazardous scaffolding for wall thickness audits.",
             "A vertical-climbing magnetic crawler adhering to steel tank walls taking ultrasonic thickness scans.",
             "Oil refineries, thermal power plants, chemical storage yards.", "$3B tank inspection market.",
             "Neodymium Magnetic Wheels, Ultrasonic Gauge, Jetson Nano.", "Automated wall thickness heatmap rendering algorithm.",
             "Inspection audit service fee (₹60,000 per storage tank audit).", "Magnetic traction slip on painted tank surfaces.",
             "Month 1-2: Magnetic climbing chassis build. Month 3: Refinery tank trial. Month 4+: Audit sales.", "Technology Development Board.", "ASME Boiler & Pressure Vessel Code."),
        ]
    },
    {
        "subtopic": "mobile robots",
        "category_slug": "robotics",
        "industry": "Robotics & Automation",
        "items": [
            ("Autonomous Mobile Robot (AMR) for Warehouse Logistics", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-high"],
             "E-commerce fulfillment warehouses suffer high labor turnover during manual order cart hauling.",
             "A LiDAR-guided Autonomous Mobile Robot (AMR) hauling 200kg payloads between warehouse racks.",
             "3PL logistics providers, e-commerce warehouses, auto plants.", "$18B AMR warehouse market.",
             "2D LiDAR, ROS2 Nav2, BLDC Motors, STM32, Web Dashboard.", "SLAM dynamic obstacle avoidance and fleet multi-robot routing.",
             "AMR unit sale (₹3.5 Lakhs) or RaaS (₹18,000/month).", "LiDAR localization accuracy in dynamic environments.",
             "Month 1-2: AMR chassis & ROS2 Nav2 tuning. Month 3: Warehouse pilot. Month 4-6: Commercial launch.", "MeitY Robotics Grant.", "ANSI/RIA R15.08 Mobile Robot Standard."),
            ("Factory Floor Automated Guided Vehicle (AGV) Tugger", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Automotive assembly plants move heavy component bins across shop floors using manual forklift drivers.",
             "A magnetic tape / optical line follower AGV tugger pulling 500kg material carts along fixed factory routes.",
             "Auto assembly plants, appliance manufacturers, steel fabricators.", "$10B AGV tugger market.",
             "Magnetic Line Sensor, Industrial PLC, BLDC Drive, Safety Laser.", "Automated line intersection traffic management PLC algorithm.",
             "AGV Tugger unit sale (₹2.8 Lakhs/unit).", "Emergency safety bumper stop reliability.",
             "Month 1-2: AGV chassis & magnetic guide build. Month 3: Auto plant trial. Month 4+: Factory sales.", "Make in India Robotics.", "ISO 3691 Industrial Truck Safety."),
            ("Hospital Disinfection & Payload Delivery Mobile Robot", "₹7 Lakh (Under 10 Lakhs)", "beginner", ["investment-low", "ai-high"],
             "Hospitals need automated surface UV disinfection and contactless medical supply delivery to isolation wards.",
             "An autonomous AMR equipped with UV-C lamps and a lockable medicine cabinet navigating hospital corridors.",
             "Private hospitals, isolation wards, medical research facilities.", "$5B medical robotics market.",
             "LiDAR, UV-C Lamps, ROS2, Lockable Servo Drawers, Touchscreen.", "Corridor SLAM navigation with human collision avoidance.",
             "Hospital robot unit sale (₹2.9 Lakhs) or monthly rental.", "UV-C light safety cutoff when humans approach.",
             "Month 1-2: Hospital AMR build & UV-C safety. Month 3: Hospital ward trial. Month 4+: Sales.", "BIRAC HealthTech Grant.", "ISO 13485 Medical Quality."),
        ]
    },
    {
        "subtopic": "robotic welding",
        "category_slug": "robotics",
        "industry": "Robotics & Automation",
        "items": [
            ("Compact Robotic Arm Welding Cell for Auto Parts", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-hybrid"],
             "Small auto-component machine shops face severe shortages of certified MIG/TIG welders.",
             "A turnkey 6-axis robotic welding cell with pre-programmed weld trajectories delivering consistent welds.",
             "Auto tier-2 suppliers, sheet metal fabricators, bicycle makers.", "$9B robotic welding market.",
             "6-Axis Robotic Arm, MIG Power Source, Teach Pendant, Pneumatics.", "Computer vision seam tracking AI adjusting torch position.",
             "Robotic welding cell installation (₹8.5 Lakhs) + maintenance.", "EM shielding for control electronics near welding arcs.",
             "Month 1-2: Robotic arm & MIG integration. Month 3: Auto shop trial. Month 4+: Machine sales.", "ATUFS Scheme.", "AWS D1.1 Structural Welding Code."),
            ("Structural Steel Automated Cobot Welding Station", "₹9 Lakh (Under 10 Lakhs)", "advanced", ["investment-low", "ai-hybrid"],
             "Structural steel fabricators spend weeks manually welding large I-beams and truss joints.",
             "A collaborative robot (Cobot) mounted on a magnetic track that welders can program in 5 minutes via drag-to-teach.",
             "Structural steel fabricators, PEB manufacturers, shipyards.", "$7B cobot welding market.",
             "6-Axis Cobot Arm, Drag-to-Teach Sensor, Torch Weaver.", "Automated torch weaving pattern generator (Zig-Zag/Triangle).",
             "Cobot station sale (₹8.9 Lakhs per cell).", "Cobot payload capacity during heavy cable drag.",
             "Month 1-2: Cobot drag-to-teach interface build. Month 3: Steel plant trial. Month 4+: Sales.", "Make in India Capital Goods Scheme.", "ISO 15614 Welding Standard."),
            ("Pipe Joint Orbital Robotic Welding Rig", "₹8 Lakh (Under 10 Lakhs)", "intermediate", ["investment-low", "ai-hybrid"],
             "Oil & gas pipeline contractors struggle to achieve 100% X-ray defect-free orbital pipe welds manually.",
             "A clamp-on orbital robotic welding head that rotates around stationary pipes executing TIG root welds.",
             "Pipeline contractors, refinery builders, dairy plant installers.", "$4B orbital welding market.",
             "Orbital Weld Head, Stepper Rotation Motor, TIG Inverter, Microcontroller.", "Real-time arc voltage control (AVC) maintaining arc length.",
             "Orbital welding rig sale (₹4.2 Lakhs/rig).", "Pipe ovality misalignment compensation.",
             "Month 1-2: Orbital head mechanical rig build. Month 3: Pipeline contractor trial. Month 4+: Sales.", "Technology Development Board.", "ASME Section IX Welding Qualification."),
        ]
    },
]


def _build_article_specs() -> list[dict]:
    specs = []
    idx = 1
    for group in SUBTOPIC_IDEAS_DATABASE:
        subtopic_tag = group["subtopic"]
        category_slug = group["category_slug"]
        industry = group["industry"]

        for item in group["items"]:
            title, investment, difficulty, extra_tags, problem, solution, target_cust, market_opp, tech_stack, ai_opp, rev_model, challenges, roadmap, schemes, refs = item

            # Combine tags ensuring subtopic tag is explicitly included
            all_tags = list(set([subtopic_tag] + extra_tags + [industry.lower()]))

            content_markdown = f"""# {title}

**Industry:** {industry}  
**Subtopic:** {subtopic_tag.title()}  
**Estimated Investment:** {investment}  
**Difficulty:** {difficulty.capitalize()}  
**Keywords:** {', '.join(all_tags)}  

## Problem Statement
{problem}

## Solution
{solution}

## Target Customers
{target_cust}

## Market Opportunity
{market_opp}

## Estimated Investment & Financial Plan
- **Total Estimated Capital:** {investment}
- **Equipment & Infrastructure:** Machinery procurement, lab tooling, workspace setup.
- **Working Capital:** Initial 3-month raw material inventory and operating buffer.
- **Unit Economics:** High margin structure with clear path to cash flow positivity within 6 to 9 months.

## Technology Stack
{tech_stack}

## AI & Automation Opportunities
{ai_opp}

## Revenue Model
{rev_model}

## Challenges & Risk Mitigation
{challenges}

## Implementation Roadmap
{roadmap}

## Government Schemes & Subsidies
{schemes}

## References & Industry Standards
{refs}
"""
            specs.append({
                "title": title,
                "summary": solution,
                "content": content_markdown,
                "category_slug": category_slug,
                "tags": all_tags,
                "difficulty": difficulty,
                "thumbnail": _thumb(category_slug, idx),
                "views": (idx * 23) % 450 + 50,
            })
            idx += 1
    return specs


RESOURCE_SPECS = [
    ("Startup India Hub", "Official portal for DPIIT recognition, tax benefits, and government schemes.", "https://www.startupindia.gov.in/", "tool", "company-registration", True),
    ("MSME Samadhaan & Udyam Portal", "Government MSME registration and credit schemes.", "https://udyamregistration.gov.in/", "tool", "manufacturing-industry-4-0", True),
    ("BIRAC Biotechnology Innovation Grants", "Biotech and healthtech funding programmes.", "https://birac.nic.in/", "article", "healthcare", True),
    ("Make in India Portal", "Manufacturing incentives and industrial sector policies.", "https://www.makeinindia.com/", "tool", "manufacturing-industry-4-0", True),
    ("CDSCO Medical Devices Portal", "Regulatory guidance for healthtech devices.", "https://cdsco.gov.in/", "article", "healthcare", False),
    ("NITI Aayog EV Guidelines", "Electric Vehicle policies and battery swapping framework.", "https://www.niti.gov.in/", "article", "renewable-energy", True),
    ("ICAR Agricultural Research Library", "Agri-tech standards and ICAR technologies.", "https://icar.org.in/", "article", "agriculture", False),
    ("FSSAI Food Safety Regulations", "Food processing licenses and safety guidelines.", "https://fssai.gov.in/", "tool", "food-processing", True),
]


def seed() -> None:
    settings = get_settings()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = AuthService.ensure_admin_user(
            db,
            email=settings.admin_email,
            password=settings.admin_password,
            full_name="Platform Admin",
        )

        # Idempotent reset of categories, articles, resources
        db.execute(delete(Article))
        db.execute(delete(Resource))
        db.execute(delete(Category))
        db.commit()

        slug_to_category: dict[str, Category] = {}
        for spec in CATEGORIES:
            cat = Category(**spec)
            db.add(cat)
            db.flush()
            slug_to_category[cat.slug] = cat
        db.commit()

        for i, spec in enumerate(_build_article_specs()):
            difficulty = ArticleDifficulty(spec["difficulty"])
            published_at = datetime.now(timezone.utc) - timedelta(days=(120 - i))
            article = Article(
                title=spec["title"],
                slug=slugify(spec["title"]),
                summary=spec["summary"],
                content=spec["content"],
                category_id=slug_to_category[spec["category_slug"]].id,
                author_id=admin.id,
                status=ArticleStatus.published,
                difficulty=difficulty,
                estimated_reading_time=estimate_reading_time(spec["content"]),
                thumbnail=spec["thumbnail"],
                tags=spec["tags"],
                view_count=spec["views"],
                published_at=published_at,
            )
            db.add(article)
        db.commit()

        for i, (title, description, url, rtype, cat_slug, featured) in enumerate(RESOURCE_SPECS):
            if cat_slug in slug_to_category:
                db.add(
                    Resource(
                        title=title,
                        description=description,
                        url=url,
                        type=ResourceType(rtype),
                        category_id=slug_to_category[cat_slug].id,
                        is_featured=featured,
                        thumbnail=_thumb(cat_slug, 300 + i),
                    )
                )
        db.commit()

        cats = db.scalar(select(func.count()).select_from(Category)) or 0
        arts = db.scalar(select(func.count()).select_from(Article)) or 0
        ress = db.scalar(select(func.count()).select_from(Resource)) or 0
        print(f"Seeded {cats} categories, {arts} rich startup & manufacturing ideas, {ress} resources.")

        # Trigger RAG re-indexing automatically
        try:
            from app.rag.ingest import rebuild_vector_index
            rebuild_vector_index()
        except Exception as e:
            print("Automatic RAG reindexing warning:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed()

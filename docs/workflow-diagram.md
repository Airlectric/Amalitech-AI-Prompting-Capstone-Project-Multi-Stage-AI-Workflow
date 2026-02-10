# Automated Intelligent Data Analysis Pipeline - Workflow Diagram

```mermaid
flowchart TD
    subgraph Input
        CSV[Raw CSV File]
    end

    subgraph Stage0[Stage 0: Profiler]
        P[profiler.py]
        P --> |data_profile JSON| Stage1
    end

    subgraph Stage1[Stage 1: Gemini Analyst]
        G1[gemini_client.py<br/>analyze_data()]
        G1 --> |analysis_plan JSON| Stage2
    end

    subgraph Stage2[Stage 2: Groq Coder]
        GR[groq_client.py<br/>generate_code()]
        GR --> |Python script| Stage3
    end

    subgraph Stage3[Stage 3: Executor]
        E[executor.py<br/>run_analysis()]
        E --> |Charts + Results| Stage4
    end

    subgraph Stage4[Stage 4: Gemini Narrator]
        G2[gemini_client.py<br/>narrate_results()]
        G2 --> |narrative JSON| Stage5
    end

    subgraph Stage5[Stage 5: Compiler]
        C[compiler.py<br/>build_report()]
        C --> |HTML Report| Output
    end

    CSV --> P
    Stage1 --> G1
    Stage2 --> GR
    Stage3 --> E
    Stage4 --> G2
    Stage5 --> C

    subgraph Output
        Report[report.html]
        Charts[PNG Charts]
    end

    C --> Report
    E --> Charts

    classDef gemini fill:#4285F4,stroke:#333,stroke-width:2px,color:white
    classDef groq fill:#FF6B35,stroke:#333,stroke-width:2px,color:white
    classDef python fill:#3776AB,stroke:#333,stroke-width:2px,color:white
    classDef io fill:#FFD43B,stroke:#333,stroke-width:2px,color:#333

    class Stage1,G1,G2 gemini
    class Stage2,GR groq
    class Stage0,P,Stage3,E,Stage4,Stage5,C python
    class Input,CSV,Output,Report,Charts io
```

## Legend
- **Blue**: Gemini API stages
- **Orange**: Groq API stage
- **Green**: Python modules
- **Yellow**: Input/Output

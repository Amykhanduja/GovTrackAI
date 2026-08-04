# Intelligent Document Processing Pipeline

## Architecture
Every downloaded document flows through `ai/pipeline.py`. 
The `DocumentProcessingPipeline` is a unified orchestrator that routes text through decoupled AI and heuristic modules.

## Pipeline Stages
1. **ParserFactory**: Identifies file extension and routes to appropriate `parsers/*_parser.py`.
2. **DocumentClassifier**: Aborts processing if the document is merely an Admit Card or Result notice.
3. **AIDuplicateDetector**: Computes text signature to block identical PDFs posted on different dates.
4. **InformationExtractor & DateExtractor**: Pulls raw structured data (vacancies, salaries, age).
5. **EligibilityExtractor**: Identifies mandatory degree and branch requirements.
6. **JobClassifier & KeywordExtractor**: Tags the job for the searchable index.
7. **DocumentSummarizer**: Generates a 2-sentence summary.
8. **EligibilityChecker**: Compares the user profile config against the `EligibilityExtractor` output.
9. **PriorityScorer**: Calculates a 0-100 score based on eligibility and keywords.

## Extension
To add new AI logic (e.g., LLM-based API calls), modify the respective class in `ai/` without breaking the `DocumentProcessingPipeline` contract.

import http from "node:http";

interface AnalysisRequest {
  resume: string;
  job_description: string;
}

interface AnalysisResponse {
  match_score: number;
  summary: string;
  strengths: string[];
  gaps: string[];
  missing_keywords: string[];
  improvements: string[];
  interview_likelihood: string;
  one_line_verdict: string;
  score_label?: string;
}

async function analyzeResume(
  request: AnalysisRequest,
  baseUrl: string = "http://127.0.0.1:8000",
): Promise<AnalysisResponse> {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify(request);
    const options = {
      hostname: "0.0.0.0",
      port: 8001,
      path: "/analyze",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(body),
      },
    };
    const req = http.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => {
        data += chunk;
      });
      res.on("end", () => {
        try {
          resolve(JSON.parse(data) as AnalysisResponse);
        } catch {
          reject(new Error("Failed to parse response"));
        }
      });
    });
    req.on("error", reject);
    req.write(body);
    req.end();
  });
}

function formatAnalysis(result: AnalysisResponse): void {
  console.log("\n=== Resume Analysis ===");
  console.log(
    `Match score: ${result.match_score}/100 (${result.score_label ?? ""})`,
  );
  console.log(`Likelihood: ${result.interview_likelihood}`);
  console.log(`Verdict: ${result.one_line_verdict}`);
  console.log("\nStrengths:");
  result.strengths.forEach((s, i) => console.log(`  ${i + 1}. ${s}`));
  console.log("\nGaps:");
  result.gaps.forEach((g, i) => console.log(`  ${i + 1}. ${g}`));
  console.log("\nMissing keywords:", result.missing_keywords.join(", "));
}

const testRequest: AnalysisRequest = {
  resume: `Rashmitha - Btech CSE 2026 Hyderabad
    Skills: Python,FastAPI,Langchain,RAG,ChromaDB,
    TypeScript (learning) ,Docker (learning), Gemini API
    Projects: AI Chatbot, Resume Analyzer, RAG system, Multi-agent pipeline with LangGraph`,

  job_description: `AI Engineer- 0-2 years
    Requirements: Python,FastAPI,LangChain, Docker, TypeScript
    Nice to have: RAG, vector Databases, CI/CD`,
};

console.log("Calling resume analyzer API...");
analyzeResume(testRequest)
  .then(formatAnalysis)
  .catch((err) => console.error("API Error:", err.message));

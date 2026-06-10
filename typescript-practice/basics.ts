const greet = (name: string, role: string = "developer"): string => {
  return `Hello ${name}, you are a ${role}`;
};

console.log(greet("Rashmitha", "AI Engineer"));

interface Skill {
  name: string;
  level: "beginner" | "intermediate" | "expert";
  yearsOfExperience: number;
}

interface Developer {
  name: string;
  skills: Skill[];
  location: string;
  isAvailable: boolean;
}

const rashmitha: Developer = {
  name: "Rashmitha",
  skills: [
    { name: "Python", level: "expert", yearsOfExperience: 2 },
    { name: "FastAPI", level: "intermediate", yearsOfExperience: 0.5 },
    { name: "LangChain", level: "intermediate", yearsOfExperience: 0.5 },
    { name: "TypeScript", level: "beginner", yearsOfExperience: 0 },
  ],
  location: "Hyderabad",
  isAvailable: true,
};

function getExpertSkills(dev: Developer): string[] {
  return dev.skills
    .filter((s: Skill) => s.level === "expert")
    .map((s: Skill) => s.name);
}

function addSkill(dev: Developer, skill: Skill): Developer {
  return { ...dev, skills: [...dev.skills, skill] };
}

console.log("Expert skills:", getExpertSkills(rashmitha));

const updated = addSkill(rashmitha, {
  name: "Docker",
  level: "beginner",
  yearsOfExperience: 0,
});

console.log(
  "Skills after adding Docker:",
  updated.skills.map((s) => s.name),
);

type ApiResponse = {
  data: any;
  status: number;
  message: string;
  timestamp: string;
};

async function mockApiCall(endpoint: string): Promise<ApiResponse> {
  return {
    data: rashmitha,
    status: 200,
    message: "Success",
    timestamp: new Date().toISOString(),
  };
}

try {
  // Line execution will pause here until the promise resolves, matching a linear workflow
  const res = await mockApiCall("/api/developer");

  console.log(`API response [${res.status}]: ${res.message}`);
  console.log("Developer:", res.data.name, "from", res.data.location);
} catch (error) {
  // If the promise rejects, execution jumps here instantly
  console.error("API call failed:", error);
}

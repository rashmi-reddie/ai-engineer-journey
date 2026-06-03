import os
import json
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

LOG_FILE="learning_log.json"

class LearningLogger:
    def __init__(self):
        self.entries=self.load()
        self.client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.config=types.GenerateContentConfig(
            system_instruction="""
            You are a learning coach reviewing a student's daily learning log. Give encouraging ,Specific, actionable feeback.
            Point out patterns,suggest connection between topics,and recommend what to focus on next. Keep it under 100 words."""
            
        )
        
    def load(self):
        try:
            with open(LOG_FILE,"r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print("Log file corrupted. Starting fresh.")
            return []
    
    def _save(self):
        with open(LOG_FILE,"w") as f:
            json.dump(self.entries,f,indent=2)
            
    def add_entry(self,day,topic,what_i_learned,what_confused_me,project_built):
        entry={
            "day":day,
            "date":datetime.now().strftime("%Y-%m-%d"),
            "topic":topic,
            "learned":what_i_learned,
            "confused":what_confused_me,
            "project":project_built,
            "timestamp":datetime.now().isoformat()
            
        }
        self.entries.append(entry)
        self._save()
        print(f"Day {day} entry saved.")
        return entry
    
    def show_all(self):
        if not self.entries:
            print("NO entries yet.")
            return
        for e in self.entries:
            print(f"\nDay {e['day']} - {e['date']} - {e['topic']}")
            print(f" Learned: {e['learned'][:80]}...")
            print(f"Built: {e['project']}")
            
    def search(self,keyword):
        keyword=keyword.lower()
        results=[
            e for e in self.entries
            if keyword in e['learned'].lower()
            or keyword in e['topic'].lower()
            or keyword in e["project"].lower()
        ]
        print(f"\n Found {len(results)} entries matching '{keyword}':")
        for e in results:
            print(f" Day {e['day']}: {e['topic']} - {e['project']}")
        return results
    def get_ai_feedback(self):
        if not self.entries:
            print("Add some entries first.")
            return
        recent=self.entries[-3:]
        summary="\n".join([
            f"Day {e['day']} ({e['topic']}): learned {e['learned']}."
            f"Confused by: {e['confused']}. Built: {e['project']}."
            for e in recent
        ])
        prompt=f"Here are my last {len(recent)} learning log entries:\n\n{summary}"
        response=self.client.models.generate_content(
            model="gemini-2.5-flash",
            config=self.config,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            ]
            )
        print("\nAI Coach Feedback:")
        print(response.text)
    
    def get_stats(self):
        if not self.entries:
            print("No entries yet.")
            return
        topics=[e["topic"] for e in self.entries]
        print(f"\n Total days logged: {len(self.entries)}")
        print(f"Topics covered: {', '.join(set(topics))}")
        confused_entries=[e for e in self.entries if len(e["confused"])>10]
        print(f"Days with confusion logged: {len(confused_entries)}")
        
def main():
    logger=LearningLogger()
    print("\nLearning Logger - 90-day AI Engineering Journey")
    print("Commands: add,show,search,feedback,stats,quit\n")
    while True:
        cmd=input("command: ").strip().lower()
         
        if cmd=="quit":
            break
        elif cmd=="add":
            day=input("Day number: ").strip()
            topic=input("Topic (e.g. FastAPI, Python OOP): ").strip()
            learned=input("What did you learn? ").strip()
            confused=input("what confused you?").strip()
            project=input("What did you build?").strip()
            logger.add_entry(day,topic,learned,confused,project)
        elif cmd=="show":
            logger.show_all()
        elif cmd=="search":
            keyword=input("Search keyword: ").strip()
            logger.search(keyword)
        elif cmd=="feedback":
            print("Getting AI feedback on your recent progress...")
            logger.get_ai_feedback()
        elif cmd=="stats":
            logger.get_stats()
        else:
            print("Unknown command. Try: add, show,search,feedback,stats,quit")
            
if __name__=="__main__":
    main()
         
        
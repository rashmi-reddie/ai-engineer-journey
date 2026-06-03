messages=[
   {"role": "user", "parts": ["hello","hi"]},
    {"role": "model", "parts": ["hi there"]},
    {"role": "user", "parts": ["what is python?"]},
    {"role": "model", "parts": ["python is a language"]}, 
]
user_messages=[m["parts"][0] for m in messages if m['role']=="user"]
print("User Messges:",user_messages)

lengths=[len(m["parts"][0]) for m in messages]
print("Messages lengths:",lengths)

upper_replies=[m['parts'][0].upper() for m in messages if m["role"]=="user"]
print("Uppercase replies:",upper_replies)

word_counts={m["role"]: len(m["parts"][0].split()) for m in messages}
print("word counts by role:",word_counts)

long_messages=[m for m in messages if len(m["parts"][0])>10]
print("long messages count:",len(long_messages))

nested=[[1,2],[3,4],[5,6]]
flat=[num for sublist in nested for num in sublist]
print("Flattened:",flat)
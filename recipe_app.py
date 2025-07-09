import tkinter as tk
from tkinter import messagebox
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load and clean recipe data
recipe_df = pd.read_csv("recipes.csv")
recipe_df.columns = recipe_df.columns.str.strip()

# TF-IDF-based recipe recommendation with score filtering
def recommend_recipes(user_input):
    ingredients = recipe_df['Ingredient'].tolist()
    all_text = ingredients + [user_input]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_text)
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]

    # Filter non-zero similarity scores
    indexed_scores = [(i, score) for i, score in enumerate(cosine_sim) if score > 0]
    if not indexed_scores:
        return pd.DataFrame(columns=['Recipe', 'Ingredient', 'Procedure'])

    top_indices = sorted(indexed_scores, key=lambda x: x[1], reverse=True)[:5]
    indices = [i for i, _ in top_indices]
    return recipe_df.iloc[indices][['Recipe', 'Ingredient', 'Procedure']]

# GUI setup
root = tk.Tk()
root.title("AI Recipe Recommender")
root.geometry("800x600")
root.configure(bg="#f7f9fc")  # professional soft gray-blue

# Header
tk.Label(root, text="AI Recipe Recommender", font=("Helvetica", 22, "bold"),
         bg="#f7f9fc", fg="#2c3e50").pack(pady=10)
tk.Label(root, text="Enter your available ingredients or preferences:",
         font=("Arial", 12), bg="#f7f9fc", fg="#2c3e50").pack()

# Horizontal input frame
input_frame = tk.Frame(root, bg="#f7f9fc")
input_frame.pack(pady=10)

entry = tk.Entry(input_frame, width=50, font=("Arial", 12))
entry.pack(side="left", padx=(0, 10))

recommend_btn = tk.Button(input_frame, text="Recommend Recipes", command=lambda: recommend_button_clicked(),
                          bg="#1a73e8", fg="white", font=("Arial", 12, "bold"), padx=10, pady=3)
recommend_btn.pack(side="left")

# Scrollable result frame
canvas = tk.Canvas(root, bg="#f7f9fc", highlightthickness=0)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scroll_frame = tk.Frame(canvas, bg="#f7f9fc")
canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
result_frame = scroll_frame

# Track the currently opened procedure
opened_label = None

# Toggle visibility and auto-close others
def toggle_show(label):
    global opened_label
    if opened_label and opened_label != label:
        opened_label.pack_forget()
    if label.winfo_ismapped():
        label.pack_forget()
        opened_label = None
    else:
        label.pack(padx=10, pady=5)
        canvas.yview_moveto(1.0)
        opened_label = label

# Recipe recommendation logic
def recommend_button_clicked():
    global opened_label
    opened_label = None
    user_input = entry.get().strip()
    if not user_input:
        messagebox.showwarning("Input Required", "Please enter your ingredient or preference.")
        return

    results = recommend_recipes(user_input)

    # Clear previous results
    for widget in result_frame.winfo_children():
        widget.destroy()

    if results.empty:
        tk.Label(result_frame, text="⚠️ No matching recipes found.",
                 font=("Arial", 13), bg="#f7f9fc", fg="red").pack(pady=20)
        return

    tk.Label(result_frame, text="🔍 Top Recipe Recommendations",
             font=("Helvetica", 16, "bold"), bg="#f7f9fc", fg="#2c3e50").pack(pady=10)

    for _, row in results.iterrows():
        recipe_name = row['Recipe']
        ingredients = row['Ingredient']
        procedure = row['Procedure']

        # Card style
        card = tk.Frame(result_frame, bg="#e3eaf2", bd=1, relief="solid")
        card.pack(fill="x", padx=30, pady=10)

        title = tk.Label(card, text=recipe_name, font=("Arial", 14, "bold"),
                         bg="#cfd8dc", fg="#2c3e50", pady=5)
        title.pack(fill="x")

        proc_label = tk.Label(card,
            text=f"\n📋 Ingredients: {ingredients}\n\n🍳 Procedure:\n{procedure}",
            font=("Arial", 11), bg="#f7f9fc", fg="#2c3e50", justify="left", wraplength=700)
        proc_label.pack_forget()

        title.bind("<Button-1>", lambda e, lbl=proc_label: toggle_show(lbl))

root.mainloop()

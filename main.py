# Smart User Profile Generator
# Python Developer Internship - Task 1

# Display welcome message
print("=" * 50)
print("       Smart user  PROFILE GENERATOR")
print("=" * 50)
print()

# Collect user information
full_name = input("Enter your full name: ")
age = input("Enter your age: ")
city = input("Enter your city: ")
profession = input("Enter your profession / field of study: ")
fav_language = input("Enter your favorite programming language: ")
bio = input("Enter a short bio (1-2 lines): ")

# Convert age to integer using type casting
age = int(age)

# Format the output
print()
print("-" * 35)
print("       USER PROFILE SUMMARY")
print("-" * 35)
print(f"Name: {full_name}")
print(f"Age: {age}")
print(f"City: {city}")
print(f"Profession: {profession}")
print(f"Favorite Language: {fav_language}")
print()
print("Bio:")
print(bio)
print("-" * 35)
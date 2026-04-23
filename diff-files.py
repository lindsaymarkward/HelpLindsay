import os
from difflib import SequenceMatcher


def main():
    # print(os.getcwd())
    directories = ("one", "two")
    similarities = []
    for filename in os.listdir(directories[0]):
        # print(filename)
        try:
            similarity = get_similarity(f"{directories[0]}/{filename}", f"{directories[1]}/{filename}")
            similarities.append(similarity)
            print(f"Similarity: {similarity:.2%}")
        except:
            continue
        number_of_files = len(similarities)
    average = sum(similarities) / number_of_files
    print(f"Average over {number_of_files} files is {average:.2%}")


def get_similarity(file1, file2):
    with open(file1) as f1, open(file2) as f2:
        text1, text2 = f1.read(), f2.read()
    return SequenceMatcher(None, text1, text2).ratio()


main()

from collections import defaultdict
import pickle
import sys

def wordValidForResult(guess, word, result):
    greenPos = [x for x in range(5) if result[x] == "g"]

    word = list(word)

    for pos in greenPos:
        if guess[pos] != word[pos]:
            return False
        else:
            word[pos] = "_"

    yellowPos = [x for x in range(5) if result[x] == "y"]

    for pos in yellowPos:
        if guess[pos] == word[pos]:
            return False
        elif guess[pos] not in word:
            return False
        else:
            ind = word.index(guess[pos])
            word[ind] = "_"

    blackPos = [x for x in range(5) if result[x] == "b"]

    for pos in blackPos:
        if guess[pos] in word:
            return False

    return True

def numEliminated(guess, word, possible, elimPerWord):
    result = ["b"] * 5
    wordList = list(word)
    guessList = list(guess)

    matchingPos = [x for x in range(5) if guessList[x] == wordList[x]]

    for pos in matchingPos:
        result[pos] = "g"
        wordList[pos] = "_"
        guessList[pos] = "_"

    for pos in range(5):
        if guessList[pos] in wordList and guessList[pos] != "_":
            result[pos] = "y"
            wordList[wordList.index(guessList[pos])] = "_"
            guessList[pos] = "_"

    result = "".join(result)

    if elimPerWord[guess][result] > 0:
        return elimPerWord[guess][result]
    else:
        count = 0

        for poss in possible:
            if not wordValidForResult(guess, poss, result):
                count += 1
        elimPerWord[guess][result] = count
        return count

def nextGuess(guessSet, solutionSet):
    guess = None
    avgEliminated = 0

    elimPerWord = defaultdict(lambda: defaultdict(int))

    for g in guessSet:
        total = 0

        for word in solutionSet:
            total += numEliminated(g, word, solutionSet, elimPerWord)

        avg = total/len(solutionSet)

        if avg > avgEliminated or (avg == avgEliminated and g in solutionSet):
            avgEliminated = avg
            guess = g


    return guess


def play():
    with open("validGuesses.pkl","rb") as f:
        guessSet = pickle.load(f)

    with open("validSolutions.pkl","rb") as f:
        solutionSet = pickle.load(f)

    for i in range(6):
        print("There are " + str(len(solutionSet)) + " possible words remaining.")

        if i == 0:
            # precomputed with nextGuess
            guess = "roate"
        elif len(solutionSet) == 1 or i == 5:
            guess = next(iter(solutionSet))
        else:
            guess = nextGuess(guessSet, solutionSet)

        print("Guess " + guess)

        result = input("Enter your result as a string with g for green, y for yellow, and b for black. ")

        result = result.replace(" ", "").lower()

        if result == "ggggg":
            print("Congrats!")
            return i+1
        elif i == 5:
            print("Oops, maybe next time.")
            return False

        removeSet = set()

        for word in solutionSet:
            if not wordValidForResult(guess, word, result):
                removeSet.add(word)

        solutionSet = set([x for x in solutionSet if x not in removeSet])

        guessSet.remove(guess)

if __name__ == "__main__":
    result = play()
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--keep-stats", "-ks"]:
            try:
                with open("stats.pkl", "rb") as f:
                    stats = pickle.load(f)
            except FileNotFoundError:
                stats = {"gamesPlayed": 0, "gamesWon": 0, "averageGuesses": 0}

            stats["gamesPlayed"] += 1

            if result:
                stats["averageGuesses"] = (stats["averageGuesses"] * stats["gamesWon"] + result)/(stats["gamesWon"] + 1)
                stats["gamesWon"] += 1

            winPercent = stats["gamesWon"]*100/stats["gamesPlayed"]
            guesses = stats["averageGuesses"]

            print(f"Win percentage: {winPercent}%")
            if result:
                print(f"Average guesses: {guesses}")

            with open("stats.pkl", "wb") as f:
                pickle.dump(stats, f)

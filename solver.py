from collections import defaultdict

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

def nextGuess(guessList, solutionList):
    guess = None
    avgEliminated = 0

    elimPerWord = defaultdict(lambda: defaultdict(int))

    for g in guessList:
        total = 0

        for word in solutionList:
            total += numEliminated(g, word, solutionList, elimPerWord)

        avg = total/len(solutionList)

        if avg > avgEliminated or (avg == avgEliminated and g in solutionList):
            avgEliminated = avg
            guess = g


    return guess

import pickle

def play():
    with open("validGuesses.pkl","rb") as f:
        guessList = pickle.load(f)

    with open("validSolutions.pkl","rb") as f:
        solutionList = pickle.load(f)

    for i in range(6):
        print("There are " + str(len(solutionList)) + " possible words remaining.")

        if i == 0:
            # precomputed with nextGuess
            guess = "roate"
        elif len(solutionList) == 1 or i == 5:
            guess = next(iter(solutionList))
        else:
            guess = nextGuess(guessList, solutionList)

        print("Guess " + guess)

        result = input("Enter your result as a string with g for green, y for yellow, and b for black. ")

        result = result.replace(" ", "").lower()

        if result == "ggggg":
            print("Congrats!")
            break
        elif i == 5:
            print("Oops, maybe next time.")
            break

        removeList = set()

        for word in solutionList:
            if not wordValidForResult(guess, word, result):
                removeList.add(word)

        solutionList = set([x for x in solutionList if x not in removeList])

        guessList.remove(guess)

if __name__ == "__main__":
    play()

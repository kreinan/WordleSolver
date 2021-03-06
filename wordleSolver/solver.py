from collections import defaultdict
import pickle
import sys
import os

class Solver:

    def __init__(self):
        path, _ = os.path.split(__file__)
        dataPath = os.path.join(path, "data")
        with open(os.path.join(dataPath, "validGuesses.pkl"),"rb") as f:
            self.guessSet = pickle.load(f)

        with open(os.path.join(dataPath, "validSolutions.pkl"),"rb") as f:
            self.solutionSet = pickle.load(f)

        self.guessesRemaining = 6

    @staticmethod
    def _wordValidForResult(guess, word, result):
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

    @staticmethod
    def _getResult(guess, word):
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
        return result

    def _numEliminated(self, guess, word, elimPerWord):
        result = self._getResult(guess, word)

        if elimPerWord[guess][result] > 0:
            return elimPerWord[guess][result]
        else:
            count = 0

            for poss in self.solutionSet:
                if not self._wordValidForResult(guess, poss, result):
                    count += 1
            elimPerWord[guess][result] = count
            return count

    def nextGuess(self):
        if self.guessesRemaining == 0:
            raise ValueError("No guesses remaining")

        guess = None

        if self.guessesRemaining == 6:
            guess = "roate"
        elif self.guessesRemaining == 1 or len(self.solutionSet) < 3:
            guess = next(iter(solutionSet))
        else:
            avgEliminated = 0

            elimPerWord = defaultdict(lambda: defaultdict(int))

            for g in self.guessSet:
                total = 0

                for word in self.solutionSet:
                    total += self._numEliminated(g, word, elimPerWord)

                avg = total/len(self.solutionSet)

                if avg > avgEliminated or (avg == avgEliminated and g in self.solutionSet):
                    avgEliminated = avg
                    guess = g

        self.guessed = guess
        return guess

    def guess(self, result: str, guess: str = None) -> None:
        self.guessesRemaining -= 1

        if not self.gameOver():
            if guess is None:
                guess = self.guessed

            removeSet = set()

            for word in self.solutionSet:
                if not self._wordValidForResult(guess, word, result):
                    removeSet.add(word)

            self.solutionSet = set([x for x in self.solutionSet if x not in removeSet])

    def gameOver(self) -> bool:
        return self.guessesRemaining == 0

    @classmethod
    def play(cls):
        solver = cls()

        while not solver.gameOver():
            if len(solver.solutionSet) <= 10:
                print("There are " + str(len(solver.solutionSet)) + " possible words remaining: " + ", ".join(list(solver.solutionSet)))
            else:
                print("There are " + str(len(solver.solutionSet)) + " possible words remaining.")

            guess = solver.nextGuess()

            print("Guess " + guess)

            actualGuess = input("Which word did you guess? Leave blank if the suggested guess was used.").strip()

            while len(actualGuess) != 0 and actualGuess not in solver.guessSet:
                print("Invalid guess.")
                actualGuess = input("Which word did you guess? Leave blank if the suggested guess was used.").strip()

            if len(actualGuess) > 0:
                guess = actualGuess

            result = input("Enter your result as a string with g for green, y for yellow, and b for black. ")

            result = result.replace(" ", "").replace(",", "").lower()

            solver.guess(result, guess)

            if result == "ggggg":
                print("Congrats!")
                return 6 - solver.guessesRemaining
            elif solver.gameOver():
                print("Oops, maybe next time.")
                return False


def main():
    result = Solver.play()
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


if __name__ == "__main__":
    main()

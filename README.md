# wordle-assistant
wordleAssistant is a Python program to help you select probe words for Wordle.

Think of Wordle as a chess game.  At every move, you enter a probe word and the game replies with cues about how the letters of your probe word compare to the letters of the day's answer word.<p>
 green  : letter in correct position<br>
 yellow : letter occurs in the answer word but in a different position<br>
 gray   : letter does not appear in the answer word<p>
At any point in the game, some potential answer words have been eliminated by the cues so far.<br>
At each stage, some of the potential probe words will be more informative than others in further narrowing down the set of possible answer words.<br>
<p>
This assistant conducts look-ahead search to score each candidate probe word for its informativeness.
<p>
The assistant computes two or three scores for each candidate probe word:<br>
  -average number of remaining allowable answer words given the probe word<br>
  -maximum number of remaining allowable answer words given the probe word<br>
  -expected number of moves to find answer<br>
If your goal is to find the answer quickly on average, chose the smallest "average" score.  But this risks requiring more guesses on some days, or even running out of the 6 guesses allowed. If your goal is to make sure you don't run out of moves, choose the smallest "maximum" score.  Usually the rank ordering of probe words is well aligned under each of these scores. When there are no more than 10 possible answer words remaining, use the expected moves score to help you decide which probe word to use next.  Sometimes you have to choose between gambling on a possible answer word versus choosing a safer probe word that cannot be an answer but is maximally informative. 
<p>
Since the initial searches are only one ply deep, the scores returned are not actually optimal.  But they are close.
<p>
The possible answer words and probe words were collected from the wordle game.  The number of possible answer words is 2,315 and the number of possible probe words is 12,972. The English language has a lot of obscure words that you can enter as probes but Wordle is kind enough to select only more common words as possible answers.
<p>
wordleAssistant runs in a command line in python3.<br>
 For instructions on how to run the program, see the documentation at the beginning of /src/wordleAssistant.py
<p>
You can also run wordleAssistant to determine the best opening probe words. This calculation takes about a day to compute on a laptop.
 <p>
 

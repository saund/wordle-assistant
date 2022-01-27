
#wordleAssistant.py
#Eric Saund
#2022/01/25
#I was going to avoid wasting time on wordle but my friend Don provoked me to do this.
#
#This program is a Wordle Assistant.
#Given some set of candidate probe words and some constraints provided by responses
#to guesses, this makes a list of remaining allowable answer words, and it scores
#candidate probe words for how good a choice each one would be.
#
#There is no claim of absolute optimal scoring. In fact, the scoring function produces
#two or three scores.  One score tells average number of words that would remain as
#eligible answers after entering a probe word. The second tells the maxium number of
#words that might remain, depending on what the (undisclosed) answer word of the day
#happens to be. This score is useful to prevent running over the limit of 6 guesses.
#To compute these scores, the program initially performs one-ply search, testing
#candidate probe words against the list of possible remaining answer words.
#When the list of remaining words is small enough, the third score computed is the
#expected number of moves required to find the answer word.  This is computed by
#fully expanding the tree of next probe moves within the remaining words.


################################################################################
#
#How to use the program:
#
#1. The program runs in Python3.  Make sure Python3 is installed on your computer.
#
#2. Download the program and the following data files to a directory:
#      wordle-answer-words.text
#      wordle-probe-words.text
#      precomputed-probe-dict-raise-normal-mode.json
#      precomputed-probe-dict-raise-hard-mode.json
#
#3. In a shell window, navigate to the directory where you installed the program
#   and data files.
#   <your-dir>/> 
#
#4. Run python:
#   <your-dir>/> python
#
#5.>>> import wordleAssistant as wa
#      The import step loads two lists of words, one list of 2,315 words that can be
#      answer words, and another list of 12,970 words that can be probe words.
#      It also loads two files of precomputed scores for the recommended first probe
#      word.  The program will run without these files but it will be a lot slower.
# 
#6.>>> wa.runGame()
#
#      The user function, runGame, has two optional arguments:
#
#      runGame(hard_mode_p = False, initial_probe_word = None)
#
#      To run in Hard mode, call runGame(True).  In Hard mode, candidate probe
#      words must meet the constraints of the Wordle response cues given so far.
#
#      The initial_probe_word defaults to 'raise'.
#      This was determined to be the most informative probe word (for details, read below).
#      If you want to use a different initial probe word, enter it as the second
#      argument to runGame().
#
#      call runGame('h') to get a brief help printout.
#
#      run runGame() in conjunction with your Wordle game running in your browser.
#
#      runGame will alternately ask you to enter the probe word typed into Wordle,
#      and Wordle game responses in the form of green, yellow, and gray tile colors
#      marking your probe entry.
#      Enter response colors as a single string of five characters:
#       'r' = gReen
#       'l' = yeLLow
#       'y' = graY
#
#Example: (letting wordleAssistant assume you entered the word 'raise' as your first
#          Wordle probe word)
#
#>> wa.runGame()
#Please enter response to probe word "raise": yrlly             <---**your entry**
#Wordle game response:   "graY  gReen  yeLLow  yeLLow  graY"
#
#     wordleAssistant will proceed to compute scores for candidate probe words.
#     Usually you'll get printout within a few seconds, but sometimes when there
#     are a lot of remaining words to sort through, the computations can take
#     several minutes.
#
##############################


##############################
#
#A deeper technical dive.
#
#7.  For convenience, give the answer and probe word lists slightly shorter names.
#
#>>> answer_word_list = wa.gl_answer_word_list  
#>>> len(answer_word_list)
#2315
#>>> probe_word_list = wa.gl_probe_word_list
#>>> len(probe_word_list)
#12970
#
#8. I recommend using 'raise' as the initial probe word.
#   From running the function, wa.scoreProbeWords() on all words, this program suggests
#   the following probe words in order of score, but you can choose whatever you like.
#
#0   ['roate', 60.42462203023758, 195]
#1   ['raise', 61.00086393088553, 168]
#2   ['raile', 61.33088552915767, 173]
#3   ['soare', 62.30107991360691, 183]
#4   ['arise', 63.72570194384449, 168]
#5   ['irate', 63.7792656587473, 194]
#6   ['orate', 63.89071274298056, 195]
#7   ['ariel', 65.28768898488121, 173]
#8   ['arose', 66.02116630669546, 183]
#9   ['raine', 67.0561555075594, 195]
#10  ['artel', 67.49589632829374, 196]
#11  ['taler', 67.73693304535637, 196]
#12  ['ratel', 69.84319654427645, 196]
#13  ['aesir', 69.8829373650108, 168]
#14  ['arles', 69.89071274298057, 205]
#15  ['realo', 69.94773218142548, 176]
#16  ['alter', 69.99179265658748, 196]
#17  ['saner', 70.12570194384449, 219]
#18  ['later', 70.22332613390928, 196]
#19  ['snare', 71.09762419006479, 219]
#20  ['oater', 71.24535637149027, 195]
#
#   Lower score is better because that means on average there will be fewer possible answer
#   words remaining after the game responds to the probe.  You'll want to prune down to the
#   single daily answer word as quickly as possible.
#
#   These are the best probe words if you only want to use candidate answer words as probes.
#
#0   ['raise', 61.00086393088553, 168]
#1   ['arise', 63.72570194384449, 168]
#2   ['irate', 63.7792656587473, 194]
#3   ['arose', 66.02116630669546, 183]
#4   ['alter', 69.99179265658748, 196]
#5   ['saner', 70.12570194384449, 219]
#6   ['later', 70.22332613390928, 196]
#7   ['snare', 71.09762419006479, 219]
#8   ['stare', 71.29460043196545, 227]
#9   ['slate', 71.57278617710583, 221]
#10   ['alert', 71.59870410367171, 196]
#11   ['crate', 72.89978401727862, 246]
#12   ['trace', 74.02030237580993, 246]
#13   ['stale', 75.60388768898488, 221]
#14   ['aisle', 76.18876889848812, 196]
#15   ['learn', 76.64060475161988, 212]
#16   ['alone', 77.16328293736501, 182]
#17   ['leant', 77.26004319654427, 208]
#18   ['least', 78.18963282937365, 221]
#19   ['crane', 78.74168466522679, 263]
#20   ['atone', 78.95939524838013, 191]
#
#The entire list of all scores are in the files,
# /probe-scores-2315.text
# /probe-scores-12790.text
#
#9. Read out the wordle response, which will be something like,
#   "yellow gray gray green yellow"
#   You will convert this to a list of char, like ['l', 'y', 'y', 'r', 'l']
#
#10. Use this game response to compose a function call to ask wordleAssistant to find the
#   remaining words given the wordle response to your probe.
#
#>>> <ok_words>, <char_constraints> = wa.pruneWordsPerProbeResponse(<word_list>,
#                                                                   [<probe_word>, <char_response_list>])
#
#For char_response_list, make it match the wordle response with the following abbreviations:
#   'l' for yeLLow
#   'y' for graY
#   'r' for gReen
#
#   For example, if you use the word, 'story' for your first probe word, your function
#   call might look like this:
#
##>>> ok_words_1, ccl1 = wa.pruneWordsPerProbeResponse(answer_word_list, ['story', ['l', 'y', 'y', 'r', 'l']])
#
#11. How many words are still allowable?
#>>> len(ok_words_1)
#
#   ccl1 is a data structure the represents the character constraints obtained from
#   the game responses. Call this function to see the allowable characters for each
#   character position, and the list of required characters:
#
#   Check out what the character constraints look like after the first probe word.
#>>> wa.printCharConstraintList(ccl1)
#
#12. Compute scores for the ok words.
#>>> scores_list_1 = wa.scoreProbeWords(ok_words_1, probe_word_list)
#
#   scores_list_1 will be a list of tuples of the form,
#      (probe_word, ave_words_remaining, max_words_remaining)
#      where probe_word is a candidate for your next wordle entry.
#      By using the second argument, probe_word_list, in the function call, we consider 
#      all words in the wordle lexicon to be candidate probe words, even if they are
#      excluded by the cues. In some cases, the best word to try next is one that
#      cannot be the final answer.
#   ave_words_remaining is the average number of words that will have to be
#      eliminated to find the correct answer word, if you use the probe_word as your next guess.
#   max_words_remaining is the maximum number of words that will have to be
#      eliminated to find the correct answer word, if you use the probe_word as your
#      next guess and the answer word happens to be the buried in a pile of distractors.
#      These scores are not rigorous; they are approximations, as the function looks only
#      one ply deep.
#   Note: this function can take several minutes to run the first time when the remaining answer
#   words (i.e. ok_words_1) numbers in the tens or hundreds. It will get faster later as
#   you reduce this list.
#   This function will print out a list of the 20 best scoring words, along with their scores.
#
#13. Usually you'll want to choose the first of these words as your next probe word.
#
#14. Repeat at step 10 with your next probe word, but this time, use the remaining words
#    in the call to pruneWordsPerProbeResponse(), i.e.
#
#>>> ok_words_2, ccl2 = wa.pruneWordsPerProbeResponse(ok_words_1, [<probe_word>, <char_response_list>])
#
#    After a few iterations, the ok_words... list will be whittled down to the final answer word.
#
#15. Once you have a reduced list of possible answer words in ok_words_1 or ok_words_2,
#    you might want to restrict the probe words to possible answers. This gives you a shot
#    at nailing the answer on the next try. But if your guess is wrong you might not
#    learn as much from it as choosing from among all probe words.
#    To restrict candidate probe words to being only possible answer words,
#    pass the remaining allowable words as the candidate_probe_word_list argument,
#    like this:
##>>> scores_list_2 = wa.scoreProbeWords(ok_words_2, ok_words_2)
#
#16. Hard Mode
#    In Hard Mode, your probe word has to be one that meets the cue constraints already
#    provided by game responses.  Pass the char_constraints you have accumulated so far.
#    To obtain scores for candidate probe words, pass the most recent char_constraints_list
#    as an optional argument to the scoreProbeWords() function:
#
#>>> scores_list_2h = wa.scoreProbeWords(ok_words_2, ok_words_2, cc2)
#
################################################################################

################################################################################
#
#Program Notes:
#
#-Kudos and gratitude are due to Devang Thakkar for his Wordle Archive program,
# which lets you play past Wordle games.  This was very helpful to development of
# wordleAssistant and it helped me to understand some subtleties of how the color
#tiles work.
#https://www.devangthakkar.com/wordle_archive/
#https://github.com/DevangThakkar/wordle_archive
#
#-I tried using numpy arrays to store character constraints for efficiency, but that
# turned out to be slower than just using sets.  I didn't figure out why.
#
################################################################################


################################################################################
#
#wordleAssistant program
#

import json


########################################
#
#Central functions
#

####################
#
#globals for normal program operation
#

gl_char_set = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
               'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
               'u', 'v', 'w', 'x', 'y', 'z')

gl_correct_response = ['r', 'r', 'r', 'r', 'r']

#The number of words that are counted as a few, for purposes of deciding when
#to take the extra step of computing expected moves, and other things.
gl_few_words_len = 10

#This was determined to be the best initial probe word by running scoreProbeWords()
#on all words in probe_word_list.  That takes about 26 hours on my laptop.
#1   ['raise', 61.00086393088553, 168]
gl_first_probe_word = 'raise'


#
#
####################



#This function applies cue_list to adjust char_constraint_list and then filters
#allowable answer words.
#
#word_list is a list of remaining candidate answer words.
#cue_list a list of two entries:   [probe_word, char_response_list]
#   where probe_word is a 5-character word
#   and response list is a list of 5 cues in the set { 'r', 'l', 'y' }
#   where 'r' means gReen  - the character is in the right position
#         'l' means yeLLow - the character is in the word but not in that position
#         'y' means graY   - the character is not in the word
#char_constraint_list is a list of list:
#  char_constraint_list[0] thru char_constraint_list[4]  are sets of allowed characters
#    in each char position
#  char_constraint_list[5] is a set of characters that must appear somewhere.
#
#Returns two values:  new_allowable_word_list, new_char_constraint_list
#If you pass in a char_constraint_list that already constrains some of the characters,
#then the new_char_constraint_list returned will add constraints to that based on
#the cue_list.  This allows you to accumulate constraints for filtering qualified
#probe words in hard mode.
#It is not necessary to pass in previous cues (responses to probes) directly because
#we expect that word_list will have filtered any non-allowable words from
#previous probes.  In hard mode, this information is carried in the
#char_constraint_list argument.
def pruneWordsPerProbeResponse(word_list, cue_list, char_constraint_list = None):
    if char_constraint_list == None:
        char_constraint_list = makeCharConstraintList()
    new_char_constraint_list = updateCharConstraintList(cue_list, char_constraint_list)
    ok_words = pruneWordsPerCharConstraints(word_list, new_char_constraint_list)
    return ok_words, new_char_constraint_list


#Run through all words in candidate_probe_word_list and test as the probe word.
#For each such probe word, run through all words in remaining_word_list pretending
#it is the correct word.  For each hypothesized correct word compute the
#cue_list, and from that, a hypothetical char_constraint_list.
#Using this char_constraint_list, count how many remaining words are allowable.
#Score each probe word by the average and max number of remaining words that
#would be returned if the probe word were entered.
#If probe_word_char_constraint_list is passed, then this is used to filter the probe words
#so that they meet char constraints from previous cues.  This is used for "hard mode"
#in which you can only submit probe words that meet all cues returned by previous
#submissions.
#If the remaining_word_list is small, then in addition, compute an expected moves score,
#which is the expected moves to completion if that probe word is entered.
#Returns a list of tuple: (probe_word, ave_words_remaining, max_words_remaining)  or
#                         (probe_word, ave_words_remaining, max_words_remaining, expected_moves)
def scoreProbeWords(remaining_word_list, candidate_probe_word_list,
                    probe_word_char_constraint_list = None,
                    print_p = True):
    if len(remaining_word_list) == 0:
        return None

    #for command line feedback
    dot_freq = int(10000/len(remaining_word_list))
    probe_word_score_list = []

    #deal with hard mode
    if probe_word_char_constraint_list != None:
        qualified_candidate_probe_word_list = \
             pruneWordsPerCharConstraints(candidate_probe_word_list, probe_word_char_constraint_list)
        print('Hard Mode: pruning candidate_probe_word_list down from ' + str(len(candidate_probe_word_list)) + ' to ' + str(len(qualified_candidate_probe_word_list)) + ' candidates that meet char constraints')
    else:
        qualified_candidate_probe_word_list = candidate_probe_word_list

    #main loop over probe_words
    probe_word_count = 0
    for probe_word in qualified_candidate_probe_word_list: #consider all candidate probe words, even ones
                                                           #that are not allowable
        #print('\nprobe_word: ' + probe_word)  
        remaining_words_sum = 0
        max_remaining_words = 0
        expected_moves_sum = 0
        for hypothetical_correct_word in remaining_word_list:
            char_response_list = markProbeWordAgainstCorrectWord(probe_word, hypothetical_correct_word)
            #Only if the remaining words have been pruned down to a small number, 
            #count expected moves to answer.  This function is recursive so cannot be
            #used with a large remaining_word_list
            if probe_word in remaining_word_list and len(remaining_word_list) <= gl_few_words_len:
                expected_moves = countExpectedMovesToAnswer(probe_word, hypothetical_correct_word,
                                                            remaining_word_list)
                expected_moves_sum += expected_moves
            if char_response_list == gl_correct_response:
                continue   #the correct probe says no more remaining words
            new_remaining_word_list, new_char_constraint_list = \
                 pruneWordsPerProbeResponse(remaining_word_list,
                                            [probe_word, char_response_list])
            num_remaining_words = len(new_remaining_word_list)
            remaining_words_sum += num_remaining_words
            max_remaining_words = max(num_remaining_words, max_remaining_words)
            #print('hyp correct word: ' + hypothetical_correct_word + ' num_remaining_words:' + str(num_remaining_words) + ' : ' + str(new_remaining_word_list))

        if len(remaining_word_list) == 0:  #no valid words, return a high scoring nonsense response 
            return ['', 1000, 1000]
        ave_remaining_words = remaining_words_sum / len(remaining_word_list)
        probe_word_score = [probe_word, ave_remaining_words, max_remaining_words]
        if expected_moves_sum > 0:
            probe_word_score.append(expected_moves_sum/len(remaining_word_list))
        probe_word_count += 1
        probe_word_score_list.append(probe_word_score)

        #command line feedback
        if (len(remaining_word_list) > 50 and probe_word_count % 1000 == 0) or print_p:
            if dot_freq > 0:
                print('')
            print(str(probe_word_count) + '  ' + str(probe_word_score))
        if dot_freq > 0 and probe_word_count % dot_freq == 0:
            print('.', end='', flush=True)

    if dot_freq > 0:
        print('')
    probe_word_score_list.sort(key = lambda x: x[1])
    if print_p:
        print('top scores:')
        for score in probe_word_score_list[0:20]:
            print(str(score))
    return probe_word_score_list



#This emulates what the Wordle game does when you enter a probe word.
#This is my updated version that tries to match the actual wordle game by marking a
#probe character as yellow only if it occurs in some other column not already
#guessed correctly.
#This version marks a probe character as gray even if that character appears in another
#column where it belongs, i.e. is marked as green there.
#For example:
#  answer_word:    H E R O N
#  probe_word      E R R O R
#Actual wordle     l y r r y   There is no R (probe char) in the answer word other
#                              than the one already marked correctly.
#returns a list length 5 in the range {'r', 'l', 'y'}
def markProbeWordAgainstCorrectWord(probe_word, correct_word):
    char_response_list = []
    #first build a char_response_list marking correct chars
    for i in range(5):
        probe_char_i = probe_word[i]
        if correct_word[i] == probe_char_i:
            char_response_list.append('r')
        else:
            char_response_list.append('y')
    #now take another pass switching to response char to yellow if the
    #probe char occurs in another column that is not green
    for i in range(5):
        if char_response_list[i] == 'r':
            continue
        probe_char_i = probe_word[i]
        #look for a match to probe_char_i elsewhere in the word...
        for i_word in range(5):
            if i_word == i:
                continue
            #...as long as it is isn't already a correct match
            if correct_word[i_word] == probe_char_i and \
               char_response_list[i_word] != 'r':
                char_response_list[i] = 'l'
    return char_response_list




#create an initial char_constraint_list
#Returns: char_constraint_list:  list of length 6
#  The first 5 elements are sets of all chars, meaning that each position is
#  unconstrained and could take any char.
#  Element 6 is an empty set meaning that there is not as of yet any requirement
#  that the word take any char.
def makeCharConstraintList():
    char_constraint_list = []
    for i in range(5):
        char_constraint_list.append(set(gl_char_set))  #the elements are sets for effeciency
    char_constraint_list.append(set())
    return char_constraint_list



#Applies the character constraints in char_constraint_list to filter out unallowable
#words from word_list.
#This is the revised version that takes advantage of the fact that the required_char
#list means that a character must occur somewhere where it is not already correct.
#Returns a list of allowable words.
def pruneWordsPerCharConstraints(word_list, char_constraint_list):
    ok_words = []
    for word in word_list:
        ok_p = True
        #check if the word's chars are allowed by the char_constraint_list
        for i in range(5):
            if i >= len(word):
                print('word is too short: ' + word + ' i: ' + str(i))
                return
            char_i = word[i]
            if char_i not in char_constraint_list[i]:
                ok_p = False
                break
        if not ok_p:
            continue
        #make sure the word has any required characters looking for a placement
        any_char_seeking_replacement_p = False
        for required_char in char_constraint_list[5]:
            seeking_placement_p = True
            for i in range(5):
                #if this is the only char allowed at this word pos, then
                #it is already placed correctly
                if len(char_constraint_list[i]) == 1 and \
                   required_char in char_constraint_list[i]:
                    continue
                if word[i] == required_char:
                    seeking_placement_p = False
                    break
            if seeking_placement_p:
                any_char_seeking_replacement_p = True
                break
        if not any_char_seeking_replacement_p:
            ok_words.append(word)
    return ok_words


#This function returns a new char_constraint_list that updates the char_constraint_list
#passed according to the char_responses in cue_list.
#
#char_constraint_list is a list of set of char
#The first 5 elements are char positions, for chars allowed in that position.
#The 6th is a set of chars that the word must have in a column that is not
#correct yet.  These are characters looking for a position.
#cue_list a list of two entries:   [probe_word, char_response_list]
#where char_response_list is a list of 5 strings like   ['y', 'y', 'l', 'r', 'l']
#
#This revision takes into account that a response char is yellow l only if the
#probe char occurs elsewhere in the word *in an incorrect position*.
#The logic of this function is kind of complicated because the rules for marking
#tiles as yellow and gray are a bit subtle.  I am not 100% sure this is correct,
#but I have stopped finding failure cases after about 50 trials.
#Does not modify char_constraint_list.
def updateCharConstraintList(cue_list, char_constraint_list):
    new_char_constraint_list = [ set(pos_chrs) for pos_chrs in char_constraint_list ]
    probe_word = cue_list[0]
    char_response_list = cue_list[1]
    chars_to_consider = {}  #key = char
                            #value: count of char occurrences
    for i_pos in range(5):
        probe_char = probe_word[i_pos]
        char_response = char_response_list[i_pos]
        if char_response == 'y':        #gray - remove probe_char entirely from this position
            new_char_constraint_list[i_pos].discard(probe_char)
            #if probe_char appears elsewhere as yellow, then we cannot be safe in eliminating
            #it from other positions
            char_appears_elsewhere_y_p = False
            for i_pos2 in range(5):
                if probe_word[i_pos2] == probe_char:
                    if char_response_list[i_pos2] == 'l':
                        char_appears_elsewhere_y_p = True
                        break
            #safe to say the char is not some another position either.
            if not char_appears_elsewhere_y_p:
                for i_pos2 in range(5):
                    #don't much with a position if it is known
                    if len(new_char_constraint_list[i_pos2]) == 1:
                        continue
                    new_char_constraint_list[i_pos2].discard(probe_char)    
                    
        elif char_response == 'l':      #yellow - remove probe_char only from i_pos chars
            new_char_constraint_list[i_pos].discard(probe_char)
            #Add a char tagged as yellow to required set only if it is not accounted for
            #by a known character that is not labeled 'r' on this cue_response.
            #Example: wordle archive 159: "raise", "prong", "debts": don't add [2] 'e'
            #to the required set because it is known to occur at [4] and does not appear
            #at [4] in 'debts'
            make_required_p = True
            #but check if this char is actually accounted for by a known char
            for i_pos2 in range(5):
                if i_pos2 == i_pos:
                    continue
                ccl_ipos2 = char_constraint_list[i_pos2]
                #if i_pos2 is known to be probe_char...
                if len(ccl_ipos2) == 1 and probe_char in ccl_ipos2:
                    #...and probe_char is not at this other position in the probe word...
                    if probe_word[i_pos2] != probe_char:
                        #...then that accounts for the yellow tile
                        make_required_p = False
            if make_required_p:
                new_char_constraint_list[5].add(probe_char)
            #This could be slightly stronger by counting the number of yellows, and in 
            #principle determine that a required_char must occur in more than one position.
            
        elif char_response == 'r':      #green - only probe_char allowed in i_pos chars
            new_char_constraint_list[i_pos] = set([probe_char])
            #Do not add to required set because this char is not looking for a placement.
            #But the character can be removed from required_set *if* it does not appear
            #at some other location with a y (seeking placement) response.
            if probe_char in new_char_constraint_list[5]:
                ok_to_remove_p = True
                for i_pos2 in range(5):
                    if i_pos2 == i_pos:
                        continue
                    if char_response_list[i_pos2] != 'l':
                        continue
                    if probe_word[i_pos2] == probe_char:
                        ok_to_remove_p = False
                if ok_to_remove_p:
                    new_char_constraint_list[5].discard(probe_char)
        else:
            print('unrecognized char_response: ' + str(char_response))
            return
    return new_char_constraint_list




#This is recursive on words in word_list so cannot be used with a very long word list.
#This returns the expected number of moves to get to the answer assuming uniform
#probability of selecting every word in word_list.
#That is not perfectly right, though, because the user will more likey select the
#recommended word than other presented to them. However, at this stage, usually
#most or all of the words have approximately the same word count score, so this
#approximation of expected moves is probably pretty close.
def countExpectedMovesToAnswer(probe_word, hypothetical_correct_word, word_list,
                               move_count = 1, indent = ''):
    #indent and print statements are left over from development, and for entertainment
    #for later developers.
    #print(indent + 'counting expected moves for probe word: ' + probe_word + '  hyp_correct_word: ' + hypothetical_correct_word + '  word_list:' + str(word_list) + ' move_count: ' + str(move_count))

    probe_response = markProbeWordAgainstCorrectWord(probe_word, hypothetical_correct_word)
    if probe_response == gl_correct_response:
        #print(indent + '***probe_word: ' + probe_word + ' matches correct word, returning move_count: ' + str(move_count))
        return move_count
    move_count += 1
    reduced_word_list, ccl = pruneWordsPerProbeResponse(word_list, [probe_word, probe_response])
    #print(indent + 'reduced_word_list: ' + str(reduced_word_list))
    frac = 1/len(reduced_word_list)
    expect = 0
    for next_probe_word in reduced_word_list:
        #print(indent + 'next_probe_word: ' + next_probe_word + '  frac: ' + str(frac))
        expect += frac * countExpectedMovesToAnswer(next_probe_word, hypothetical_correct_word,
                                                    reduced_word_list, move_count, indent + '   ')
    return expect



def importWordList(word_filename = None):
    if word_filename == None:
        word_filename = gl_word_filename
    word_list = []
    with open(word_filename, encoding='utf8') as file:
        for line in file:
            if line.find('#') >= 0:
                continue
            word = line[:-1]
            if len(word) != 5:
                continue
            word_list.append(word)
    return word_list

#Collected from the wordle javascript file
#https://www.powerlanguage.co.uk/wordle/main.e65ce0a5.js
gl_probe_word_filename = 'wordle-probe-words.text'
gl_answer_word_filename = 'wordle-answer-words.text'

gl_probe_word_list = importWordList(gl_probe_word_filename)
gl_answer_word_list = importWordList(gl_answer_word_filename)


#
#
######################################## central functions

########################################
#
#Utilities for develoment
#

#score_list is a list of tuple:  (word, float average_allowable_words, float max_allowable_words)
#This returns a list of scores that have probe_word in allowable_words.
#This is useful if you want to restrict your probe word to one of the remaining allowable words
#but you want to choose the one with the best score).
def getScoresWithAllowableWords(score_list, allowable_words):
    ok_scores = []
    for score_tup in score_list:
        word = score_tup[0]
        if word in allowable_words:
            ok_scores.append(score_tup)
    return ok_scores

#This is a utility to see what scores some possible probe word have
#prints them in order of average remaining words.
def printScoresForWords(score_list, word_list):
    ok_scores = []
    for score in score_list:
        if score[0] in word_list:
            ok_scores.append(score)
    ok_scores.sort(key = lambda x: x[1])
    for score in ok_scores:
        print(str(score))


#this is a utility to see what score a probe word has
def getScoreForWord(score_list, word):
    for score in score_list:
        if score[0] == word:
            return score

#a utility for development and debugging
#enter a probe word and wordle response as a string, like
#>>> cl_raise = aw.makeCueListForResponse('raise', 'ylyyl')
#Returns a cue_list of the form ['raise', ['y', 'l', 'y', 'y', 'l']]
def makeCueListForResponse(probe_word, str_response):
    if len(probe_word) != 5 or len(str_response) != 5:
        print('probe and str_response need to be len 5')
        return
    response_list = []
    for i in range(5):
        response_list.append(str_response[i])
    return [probe_word, response_list]


#a utility for development and debugging
#cue_list_list is a list of cue_list:  [probe_word, response_list]
#This starts with the unconstrained char_constraint_list and successively applies
#the cue_lists, printing out each new_char_constraint_list along the way.
def composeCCL(cue_list_list):
    ccl_init = makeCharConstraintList()
    ccl_next = ccl_init
    for cue_list in cue_list_list:
        print('\n applying cue_list: ' + str(cue_list))
        ccl_next = updateCharConstraintList(cue_list, ccl_next)
        printCharConstraintList(ccl_next)
    return ccl_next

#char_constraint_list is a list of list
#  list[0]-list[4]  are sets of allowed characters in each char position
#  list[5] is a set of characters that must appear somewhere
def printCharConstraintList(char_constraint_list):
    for i in range(5):
        listified = list(char_constraint_list[i])
        listified.sort()
        print(str(i) + ' (' + str(listified) + ')')
    print('required: ' + str(char_constraint_list[5]))

#
#
######################################## utilities for development
        

########################################
#
#Command line game runner
#


gl_response_char_color_dict = {'r': 'gReen',
                               'l': 'yeLLow',
                               'y': 'graY'}
    

#The main user function.
def runGame(hard_mode_p = False, initial_probe_word = None):
    global gl_last_ccl
    if initial_probe_word == None:
        initial_probe_word = gl_first_probe_word
    #allow the first arg to invoke help
    if hard_mode_p in ('h', 'help', 'args', '?'):
        printHelp()

    remaining_word_list = gl_answer_word_list
    probe_word_list = gl_probe_word_list
    char_constraint_list = makeCharConstraintList()
    probe_word_scores_remaining_words = None #initialize

    #allow user input of initial probe word from the input/response loop
    if initial_probe_word == 'x':
        initial_probe_word = None
        while initial_probe_word == None:
            user_input = input('input first probe word: ')
            if user_input == '':    #exit
                return
            initial_probe_word = parseUserInputProbeWord(user_input, probe_word_list)

    #main loop
    probe_word = initial_probe_word
    user_input = 'start'  #something not ''
    round = 0
    while user_input != '':
        user_input = input('Please enter response to probe word \"' + probe_word + '\": ')
        char_response = parseUserInputToCharResponse(user_input)
        if char_response == None:
            user_input = 'retry'  #retry input of game char response
            continue
        if char_response == 'exit':
            return
        printFullColorCharResponse(char_response)
        cue_list = [probe_word, char_response]
        remaining_word_list, char_constraint_list = \
                pruneWordsPerProbeResponse(remaining_word_list, cue_list, char_constraint_list)
        gl_last_ccl = char_constraint_list  #development and debugging
        print('words_remaining: ' + str(len(remaining_word_list)))
        if len(remaining_word_list) == 0:
            print('no answer words remaining')
            return
        if len(remaining_word_list) < gl_few_words_len:
            print(str(remaining_word_list))
        if len(remaining_word_list) == 1:
            print('answer word: ' + remaining_word_list[0])
            return

        #make a flag telling whether a precomputed score dict is being used on this round
        if (hard_mode_p and \
            round == 0 and \
            probe_word == 'raise' and \
            gl_precomputed_first_probe_word_dict_raise_hard_mode != None) or \
            (not hard_mode_p and \
             round == 0 and \
             probe_word == 'raise' and \
             gl_precomputed_first_probe_word_dict_raise_normal_mode != None):
            use_dict_p = True
        else:
            use_dict_p = False
        
        #set score_char_constraint_list per hard_mode_p, and compute probe word scores accordingly
        #hard mode
        if hard_mode_p:
            score_char_constraint_list = char_constraint_list
            if use_dict_p:
                print('...looking up scores from dict (hard mode)')
                probe_word_scores = \
                    gl_precomputed_first_probe_word_dict_raise_hard_mode.get(tuple(char_response))
            else:
                if len(remaining_word_list) > 100:
                    print('many possible answer words to consider so this could take several minutes... ')
                probe_word_scores = scoreProbeWords(remaining_word_list, probe_word_list,
                                                    score_char_constraint_list, False)
            
        #normal mode
        else:
            score_char_constraint_list = None
            if use_dict_p:
                print('...looking up scores from dict (normal mode)')
                probe_word_scores = \
                    gl_precomputed_first_probe_word_dict_raise_normal_mode.get(tuple(char_response))
            else:
                if len(remaining_word_list) > 100:
                    print('...many possible answer words to consider so this could take several minutes... ')
                probe_word_scores = scoreProbeWords(remaining_word_list, probe_word_list,
                                                    score_char_constraint_list, False)

        #report scores and recommendation
        if probe_word_scores == None:
            print('no remaining answer words for this set of probes and responses')
            return

        if use_dict_p:
            print('scores from top 10 probe words:')
        else:
            print('top 10 scores from all probe words (' + str(len(probe_word_scores)) + '):')
        printProbeWordScores(probe_word_scores, 20)

        #for investigating the program's behavior
        global gl_last_probe_word_scores
        gl_last_probe_word_scores = probe_word_scores
        #
        if len(remaining_word_list) <= 40:
            #there are few enough remaining words that it is worth re-scoring them which will
            #now append expected moves"
            probe_word_scores_remaining_words = scoreProbeWords(remaining_word_list, remaining_word_list,
                                                                score_char_constraint_list, False)
        else:
            probe_word_scores_remaining_words = []
            remaining_word_set = set(remaining_word_list)
            for score in probe_word_scores:
                word = score[0]
                if word in remaining_word_set:
                    probe_word_scores_remaining_words.append(score)
        if len(probe_word_scores_remaining_words) > 0:
            print('top scores from ' + str(len(probe_word_scores_remaining_words)) + ' remaining answer words:')
            printProbeWordScores(probe_word_scores_remaining_words, gl_few_words_len)
  
        #Alert the user if they have a choice to make about picking a probe word that might
        #possibly be the answer word but on average will perform worse than a non-answer probe word.
        if probe_word_scores_remaining_words != None and \
           len(probe_word_scores_remaining_words) > 0 and \
           (probe_word_scores[0][1] < probe_word_scores_remaining_words[0][1] or \
            probe_word_scores[0][2] < probe_word_scores_remaining_words[0][2]):
            printTradeoffChoiceString(probe_word_scores[:10], probe_word_scores_remaining_words[:10],
                                      remaining_word_list)

        #iterate to next probe word
        probe_word = None
        while probe_word == None:
            user_input = input('Please enter your next probe word: ')
            if user_input == '':   #exit
                break
            probe_word = parseUserInputProbeWord(user_input, probe_word_list)
            if probe_word == 'exit':
                return
        round += 1

        
def parseUserInputToCharResponse(user_input):
    char_response = []
    user_input = user_input.lower()
    if user_input in ('q', 'quit', 'exit', 'done', 'stop'):
        return 'exit'
    if len(user_input) != 5:
        print('Please enter game response of r = green, l = yellow, y = gray for five characters')
        return None
    for i_char in range(5):
        char_i = user_input[i_char]
        if char_i not in ('r', 'l', 'y'):
            print('response characters must be one of r = green, l = yellow, y = gray')
            return None
        char_response.append(char_i)
    return char_response


def parseUserInputProbeWord(user_input, probe_word_list):
    user_input = user_input.lower()
    if user_input in ('', 'q', 'quit', 'exit', 'done', 'stop'):
        return 'exit'
    if len(user_input) != 5:
        print('Please enter a 5-character word')
        return None
    if user_input not in probe_word_list:
        print('user_input: /' + user_input + '/ not in probe_word_list')
        print('probe word must be in the list of ' + str(len(probe_word_list)) + ' probe words')
        return None
    return user_input


#char_response is a tuple of char like ('y', 'l', 'r', 'l', 'y')
def printFullColorCharResponse(char_response):

    if len(char_response) != 5:
        print('could not interpret as a color tile response: ' + char_response)
        return
    response_str = 'Wordle game response:   "'
    for response_char in char_response:
        response_str += gl_response_char_color_dict.get(response_char) + '  '
    response_str = response_str[:-2]
    print(response_str + '"')


def printProbeWordScores(probe_word_scores, num=20):
    if probe_word_scores == None or len(probe_word_scores) < 1:
        return
    has_expected_moves_p = False
    if len(probe_word_scores[0]) > 3:
        has_expected_moves_p = True
#    for score in probe_word_scores[0:20]:
#        print(str(score))
    if has_expected_moves_p:
        print(' probe       average       max       expected')
        print('  word        words       words      moves to')
        print('            remaining   remaining     answer')
        for score in probe_word_scores[0:num]:
            if len(score) > 3:
                print(' {0:8}     {1:.3f}  {2:8}         {3:.3f}'.format(score[0], score[1], score[2], score[3]))
            else:
                print(' {0:8}     {1:.3f}  {2:8}'.format(score[0], score[1], score[2]))                
    else:
        print(' probe       average       max')
        print('  word        words       words')
        print('            remaining   remaining')
        for score in probe_word_scores[0:num]:
            print(' {0:8}     {1:.3f}  {2:8}'.format(score[0], score[1], score[2]))



#Alert the user if they have a choice to make about picking a probe word that might
#possibly be the answer word but on average will perform worse than a non-answer probe word.
def printTradeoffChoiceString(top_probe_word_scores, top_answer_word_scores_remaining_words,
                              remaining_word_list):
    probe_better_list = []
    better_ave_p = False
    better_max_p = False
    for probe_word_score in top_probe_word_scores:
        probe_word = probe_word_score[0]
        probe_ave = probe_word_score[1]
        probe_max = probe_word_score [2]
        if probe_word in remaining_word_list:
            continue
        if better_ave_p and better_max_p:
            break        
        for answer_word_score in top_answer_word_scores_remaining_words:
            answer_ave = answer_word_score[1]
            answer_max = answer_word_score[2]
            if probe_ave < answer_ave and not better_ave_p:
                better_ave_p = True
                if probe_word not in probe_better_list:
                    probe_better_list.append(probe_word)

            if probe_max < answer_max and not better_max_p:
                better_max_p = True
                if probe_word not in probe_better_list:
                    probe_better_list.append(probe_word)

    probe_better_count = len(probe_better_list)
    if probe_better_count == 0:
        print('a1')
        return
    if probe_better_count == 1:
        probe_descriptor_str = 'There is a probe word* that is not a potential answer word'
    else:
        probe_descriptor_str = 'There are ' + str(probe_better_count) + ' probe words* that are not potential answer words'
    
    print('\nNotice: ' + probe_descriptor_str + ' that will leave')
    print('fewer average number of words remaining, or fewer maximum number of words remaining,')
    print('than some of the candidate answer words (bottom list).')  
    print('Decide whether to play it safe with a probe word that cannot win on the next move,')
    print('or else gamble---at the risk of taking more moves to find the answer word.')
    probe_better_words_str = ''
    for probe_better_word in probe_better_list:
        probe_better_words_str += probe_better_word + ' '
    probe_better_words_str = probe_better_words_str[:-1]
    print('*(' + probe_better_words_str + ')\n')



def printHelp():
    print('\n***Welcome to wordleAssistant ***')
    print(' args: runGame(hard_mode_p = False, initial_probe_word = None)')
    print(' To run in Hard mode, call runGame(True).')
    print(" initial_probe_word defaults to '" + gl_first_probe_word + "'.")
    print(" To enter your own initial probe word, call runGame with your word")
    print(" in quotes, like runGame(False, 'bench'), or else call as runGame(False, 'x').")
    print(' Type q to quit')


#
#
############################## game runner


##############################
#
#Precomputed dictionaries of scores for game responses to the preferred
#initial_probe_word.
#
    
        

#This precomputes the score_list the program would return when told the Wordle game's
#response to the first probe word.
#Runs through the probe_word_list (which defaults to gl_probe_word_list, but you can pass
#gl_answer_word_list as well).
#For the first_probe_word passed (which defaults to gl_first_probe_word),
#this computes the score_list for every combination of responses that the game might
#give.  The 10 best (lowest average) probe word scores are retained in a dictionary.
#returns a dict: key:    tuple: char_response
#                value:  list of score: tuple: (probe_word, ave_words_remaining, max_words_remaining)
def precomputeResponsesToFirstProbe(probe_word_list = None, first_probe_word = None, hard_mode_p = False):
    if probe_word_list == None:
        probe_word_list = gl_probe_word_list
    if first_probe_word == None:
        first_probe_word = gl_first_probe_word
    first_probe_response_dict = {}   #key:    tuple: char_response
                                     #value:  list of score
    char_response_combo_list = generateAllCharResponseCombos()
    count = 0
    for char_response_combo in char_response_combo_list:
        print(str(count) + '  ' + str(char_response_combo))
        count += 1
        cue_list = [first_probe_word, char_response_combo]
        remaining_words, char_constraint_list = pruneWordsPerProbeResponse(gl_answer_word_list, cue_list)

        #if not many remaining_words, then use only remaining words as probes
        if len(remaining_words) < gl_few_words_len:
            if hard_mode_p:
                score_list = scoreProbeWords(remaining_words, remaining_words, char_constraint_list)
            else:
                score_list = scoreProbeWords(remaining_words, remaining_words, None)
        else:
            if hard_mode_p:
                score_list = scoreProbeWords(remaining_words, probe_word_list, char_constraint_list)
            else:
                score_list = scoreProbeWords(remaining_words, probe_word_list, None)
        if score_list == None:
            continue
        print(str(char_response_combo) + ': ' + str(score_list[0:gl_few_words_len]))
        first_probe_response_dict[tuple(char_response_combo)] = score_list[0:gl_few_words_len]
    return first_probe_response_dict


def generateAllCharResponseCombos():
    combo_list = []
    for char_response in ('r', 'l', 'y'):
        combos = completePartialCombo([char_response])
        combo_list.extend(combos)
    return combo_list

#partial combo is a list of char
#Returns a list of list of char.
def completePartialCombo(partial_combo):
    if len(partial_combo) == 5:
        return [partial_combo]
    ret_list = []
    for char_response in ('r', 'l', 'y'):
        new_partial_combo = partial_combo[:]
        new_partial_combo.append(char_response)
        npc_ret = completePartialCombo(new_partial_combo)
        ret_list.extend(npc_ret)
    return ret_list


def writeProbeDictToFile(probe_dict, filename=None, header_str=''):
    if filename == None:
        filename = gl_precomputed_probe_dict_filename
    probe_dict2 = {}   
    for tup_key in probe_dict:   #need to convert keys from tuple of char to a str
        str_key = ''.join(tup_key)
        probe_dict2[str_key] = probe_dict.get(tup_key)
    with open(filename, 'w', encoding='utf8') as file:
        output_str = ''
        output_str += '#' + header_str + '\n'
        output_str += json.dumps(probe_dict2, indent=4)
        output_str += '\n'
        file.write(output_str)



def readProbeDictFromFile(filename=None):
    if filename == None:
        filename = gl_precomputed_probe_dict_filename
    with open(filename, 'r', encoding='utf8') as file:
        input_str = ''
        for line in file:
            if line.find('#') >= 0:
                continue
            if len(line) > 0:
                input_str += line
    global gl_input_str
    gl_input_str = input_str
    probe_dict2 = json.loads(input_str)
    probe_dict = {}
    for str_key in probe_dict2:
        tup_keyl = []
        for i in range(len(str_key)):
            tup_keyl.append(str_key[i])
        tup_key = tuple(tup_keyl)
        probe_dict[tup_key] = probe_dict2.get(str_key)
    print('read precomputed probe dict of size: ' + str(len(probe_dict)))
    return probe_dict


gl_precomputed_probe_dict_raise_normal_mode_filename = 'precomputed-probe-dict-raise-normal-mode.json'
gl_precomputed_probe_dict_raise_hard_mode_filename = 'precomputed-probe-dict-raise-hard-mode.json'

gl_precomputed_first_probe_word_dict_raise_normal_mode = None
gl_precomputed_first_probe_word_dict_raise_hard_mode = None


try:
    gl_precomputed_first_probe_word_dict_raise_normal_mode = \
            readProbeDictFromFile(gl_precomputed_probe_dict_raise_normal_mode_filename)
except:
    print('could not read precomputed probe dict from file ' + gl_precomputed_probe_dict_raise_normal_mode_filename)

try:
    gl_precomputed_first_probe_word_dict_raise_hard_mode = \
            readProbeDictFromFile(gl_precomputed_probe_dict_raise_hard_mode_filename)
except:
    print('could not read precomputed probe dict from file ' + gl_precomputed_probe_dict_raise_hard_mode_filename)
    

#
#
######################################## precomputed dictionaries
#
################################################################################ wordleAssistant program



################################################################################
#
#Archives
#



#This is broken
#It does not treat yellow and gray of the same character correctly.
#Example: W H E E L
#         y y l y l
def updateCharConstraintList_broken(cue_list, char_constraint_list):
    new_char_constraint_list = [ set(pos_chrs) for pos_chrs in char_constraint_list ]
    probe_word = cue_list[0]
    char_response_list = cue_list[1]
    for i_pos in range(5):
        probe_char = probe_word[i_pos]
        char_response = char_response_list[i_pos]
        if char_response == 'y':        #gray - remove probe_char entirely from positions
            for i_pos in range(5):      #       it is not already correct in or showing up as yellow
                if char_response_list[i_pos] != 'r' and char_response_list[i_pos] != 'l':
                    new_char_constraint_list[i_pos].discard(probe_char)
        elif char_response == 'l':      #yellow - remove probe_char only from i_pos chars
            new_char_constraint_list[i_pos].discard(probe_char)
            #Add a char tagged as yellow to required set only if it is not accounted for
            #by a known character that is not labeled 'r' on this cue_response.
            #Example: wordle archive 159: "raise", "prong", "debts": don't add [2] 'e'
            #to the required set because it is known to occur at [4] and does not appear
            #at [4] in 'debts'
            make_required_p = True
            #but check if this char is actually accounted for by a known char
            for i_pos2 in range(5):
                if i_pos2 == i_pos:
                    continue
                ccl_ipos2 = char_constraint_list[i_pos2]
                #if i_pos2 is known to be probe_char...
                if len(ccl_ipos2) == 1 and probe_char in ccl_ipos2:
                    #...and probe_char is not at this other position in the probe word...
                    if probe_word[i_pos2] != probe_char:
                        #...then that accounts for the yellow tile
                        make_required_p = False
            if make_required_p:
                new_char_constraint_list[5].add(probe_char)
        elif char_response == 'r':      #green - only probe_char allowed in i_pos chars
            new_char_constraint_list[i_pos] = set([probe_char])
            #Do not add to required set because this char is not looking for a placement.
            #But the character can be removed from required_set *if* it does not appear
            #at some other location with a y (seeking placement) response.
            if probe_char in new_char_constraint_list[5]:
                ok_to_remove_p = True
                for i_pos2 in range(5):
                    if i_pos2 == i_pos:
                        continue
                    if char_response_list[i_pos2] != 'l':
                        continue
                    if probe_word[i_pos2] == probe_char:
                        ok_to_remove_p = False
                if ok_to_remove_p:
                    new_char_constraint_list[5].discard(probe_char)
        else:
            print('unrecognized char_response: ' + str(char_response))
            return
    return new_char_constraint_list


def updateCharConstraintList_print(cue_list, char_constraint_list):
    new_char_constraint_list = [ set(pos_chrs) for pos_chrs in char_constraint_list ]
    probe_word = cue_list[0]
    char_response_list = cue_list[1]
    chars_to_consider = {}  #key = char
                            #value: count of char occurrences
    for i_pos in range(5):
        probe_char = probe_word[i_pos]
        #print('i_pos: ' + str(i_pos) + ' probe_char: ' + str(probe_char))
        char_response = char_response_list[i_pos]
        if char_response == 'y':        #gray - remove probe_char entirely from this position
            new_char_constraint_list[i_pos].discard(probe_char)
            #if probe_char appears elsewhere as yellow, then we cannot be safe in eliminating
            #it from other positions
            char_appears_elsewhere_y_p = False
            for i_pos2 in range(5):
                if probe_word[i_pos2] == probe_char:
                    if char_response_list[i_pos2] == 'l':
                        char_appears_elsewhere_y_p = True
                        break
            #safe to say the char is not some another position either.
            if not char_appears_elsewhere_y_p:
                for i_pos2 in range(5):
                    #don't much with a position if it is known
                    if len(new_char_constraint_list[i_pos2]) == 1:
                        continue
                    new_char_constraint_list[i_pos2].discard(probe_char)    
                    
        elif char_response == 'l':      #yellow - remove probe_char only from i_pos chars
            #print('before discarding: ' + probe_char + ' ' + str(new_char_constraint_list[i_pos]))
            new_char_constraint_list[i_pos].discard(probe_char)
            #print('after discarding: ' + probe_char + ' ' + str(new_char_constraint_list[i_pos]))
            #Add a char tagged as yellow to required set only if it is not accounted for
            #by a known character that is not labeled 'r' on this cue_response.
            #Example: wordle archive 159: "raise", "prong", "debts": don't add [2] 'e'
            #to the required set because it is known to occur at [4] and does not appear
            #at [4] in 'debts'
            make_required_p = True
            #print('yellow l  i_pos: ' + str(i_pos) + ' probe_char: ' + probe_char)
            #but check if this char is actually accounted for by a known char
            for i_pos2 in range(5):
                if i_pos2 == i_pos:
                    continue
                ccl_ipos2 = char_constraint_list[i_pos2]
                #print('ipos2: ' + str(i_pos2) + ' ' + str(ccl_ipos2))
                #if i_pos2 is known to be probe_char...
                if len(ccl_ipos2) == 1 and probe_char in ccl_ipos2:
                    #...and probe_char is not at this other position in the probe word...
                    if probe_word[i_pos2] != probe_char:
                        #...then that accounts for the yellow tile
                        make_required_p = False
            if make_required_p:
                new_char_constraint_list[5].add(probe_char)
            #This could be slightly stronger by counting the number of yellows, and in 
            #principle determine that a required_char must occur in more than one position.
            #print('after discarding 2: ' + probe_char + ' ' + str(new_char_constraint_list[i_pos]))
        elif char_response == 'r':      #green - only probe_char allowed in i_pos chars
            #print('i_pos: ' + str(i_pos) + ' char_response: ' + char_response)
            #print( ' before:' + ' ' + str(new_char_constraint_list[i_pos]))
            new_char_constraint_list[i_pos] = set([probe_char])
            #print( ' after 1:' + ' ' + str(new_char_constraint_list[i_pos]))            
            #Do not add to required set because this char is not looking for a placement.
            #But the character can be removed from required_set *if* it does not appear
            #at some other location with a y (seeking placement) response.
            if probe_char in new_char_constraint_list[5]:
                ok_to_remove_p = True
                #print('i_pos: ' + str(i_pos) + ' considering to remove probe_char: ' + probe_char + ' from required set')
                for i_pos2 in range(5):
                    if i_pos2 == i_pos:
                        #print('i_pos2 = ' + str(i_pos2))
                        continue
                    if char_response_list[i_pos2] != 'l':
                        #print('char_response_list[i_pos2]' + str(i_pos2) + ' is ' + char_response_list[i_pos2] + ' not l')
                        continue
                    if probe_word[i_pos2] == probe_char:
                        #print('probe_word[' + str(i_pos2) + '] : ' + probe_word[i_pos2] + ' == probe_char: ' + probe_char + ' so setting ok_to_remove_p = False')
                        ok_to_remove_p = False
                #print('ok_to_remove_p:' + str(ok_to_remove_p))
                if ok_to_remove_p:
                    new_char_constraint_list[5].discard(probe_char)
            #print( ' after 2:' + ' ' + str(new_char_constraint_list[i_pos]))            
        else:
            print('unrecognized char_response: ' + str(char_response))
            return
        #print('i_pos: ' + str(i_pos))
        #printCharConstraintList(new_char_constraint_list)
    #print('finally')
    #printCharConstraintList(new_char_constraint_list)
    return new_char_constraint_list




#This was my original naive version.
#See markProbeWordAgainstCorrectWord_Naive(probe_word, correct_word).
#for an explanation
#char_constraint_list is a list of list of char
#The first 5 elements are char positions, for chars allowed in that position.
#The 6th is a list of chars that the word must have somewhere.
#cue_list a list of two entries:   [probe_word, char_response_list]
#where char_response_list is a list of 5 strings like   ['y', 'y', 'l', 'r', 'l']
#This returns a new char_constraint_list that updates the char_constraint_list
#passed according to the char_responses in cue_list.
#Does not modify char_constraint_list.
def updateCharConstraintList_Naive(cue_list, char_constraint_list):
    new_char_constraint_list = [ set(pos_chrs) for pos_chrs in char_constraint_list ]
    probe_word = cue_list[0]
    char_response_list = cue_list[1]
    for i_pos in range(5):
        probe_char = probe_word[i_pos]
        char_response = char_response_list[i_pos]
        if char_response == 'y':        #gray - remove probe_char entirely
            for i_pos in range(5):
                new_char_constraint_list[i_pos].discard(probe_char)
        elif char_response == 'l':      #yellow - remove probe_char only from i_pos chars
            new_char_constraint_list[i_pos].discard(probe_char)
            new_char_constraint_list[5].add(probe_char)         #but add to required set 
        elif char_response == 'r':      #green - only probe_char allowed in i_pos chars
            new_char_constraint_list[i_pos] = set([probe_char])
            #print('r at i_pos: ' + str(i_pos) + ' nccl is: ' + str(new_char_constraint_list[i_pos]))
            new_char_constraint_list[5].add(probe_char)         #and add to required set
            #print('2r at i_pos: ' + str(i_pos) + ' nccl is: ' + str(new_char_constraint_list[i_pos]))
        else:
            print('unrecognized char_response: ' + str(char_response))
            return
        #print('i_pos: ' + str(i_pos))
        #printCharConstraintList(new_char_constraint_list)
    #print('finally')
    #printCharConstraintList(new_char_constraint_list)
    return new_char_constraint_list

#This was my original naive attempt to emulate what the Wordle game does when you
#enter a probe word.
#This version marks a character with a simple rule:
#mark as yellow if the char occurs in some other column of the word.
#But that is not quite right.  The actual wordle game marks a probe character
#as yellow only if it occurs in some other column not already guessed correctly.
#It doesn't count to mark a probe character as yellow (so it leaves it gray)
#if that character appears in another column where it belongs, so is marked
#as green there.
#Example:
#  answer_word:    H E R O N
#  probe_word      E R R O R
#This version      l l r r l
#Actual wordle     l y r r y   There is no R (probe char) in the answer word other
#                              than the one already marked correctly.
#returns a list length 5 in the range {'r', 'l', 'y'}
def markProbeWordAgainstCorrectWord_Naive(probe_word, correct_word):
    char_response_list = []
    for i in range(5):
        probe_char_i = probe_word[i]
        if correct_word[i] == probe_char_i:
            char_response_list.append('r')
        elif correct_word.find(probe_char_i) >= 0:
            char_response_list.append('l')
        else:
            char_response_list.append('y')
    return char_response_list



#This was my original naive version.
#See markProbeWordAgainstCorrectWord_Naive(probe_word, correct_word).
#Applies the character constraints in char_constraint_list to filter out unallowable
#words from word_list.
#Returns a list of allowable words.
def pruneWordsPerCharConstraints_Naive(word_list, char_constraint_list):
    ok_words = []
    for word in word_list:
        ok_p = True
        for i in range(5):
            if i >= len(word):
                print('word is too short: ' + word + ' i: ' + str(i))
                return
            char_i = word[i]
            if char_i not in char_constraint_list[i]:
                ok_p = False
                break
        for required_char in char_constraint_list[5]:
            if word.find(required_char) < 0:
                ok_p = False
                break
        if ok_p:
            ok_words.append(word)
    return ok_words



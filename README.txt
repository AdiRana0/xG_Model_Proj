
--- INSTRUCTIONS ---

# Prerequisites: 
- Python 3.10
- pip

1. Clone Repo

git clone https://github.com/yourusername/xG_Model_Proj.git
cd xG_Model_Proj


2. Create virtual environment

python -m venv venv
venv\Scripts\activate # Windows
source venv/bin/activate # macOS/Linux


3. Install dependencies

pip install -r requirements.txt


# Skip to step 7 to use pretrained model 


4. Pull data

run file 'data.py'
pulls the data from statsbomb and saves what is needed as 'data/raw_shots.csv'


5. Format data

run file 'format.py'
splits data into features and label, ready for training
saves features/label as well as feature format for later use


6. Train model

run file 'build.py'
trains the model using the data established prior
creates both logistic regression model and xgBoost model, saves LR for use in application
measures log loss and area under curve to judge model success


7. Launch application

uvicorn UI.main:app --reload


8. Open in browser

http://localhost:8000


--- PROJECT WRITE-UP ---

# Overview

xG is a statistic used in football (soccer) matches, that represents the probability of 
a shot going in. For example, a difficult shot might have an xG of 0.03, meaning the player
is expected to score that exact shot 3 times out of 100. xG is calculated by models that use
data describing the exact shot to then judge the probability of scoring. It is important to
note that this statistic is mostly used to show the difficulty of a goal on live broadcast. 
Just because the xG is 0.03 but the player scored does not mean the model is incorrect, it 
means the player scoring was 1 of the 3 times out of 100 that the shot is expected to go in. 
This project uses every shot taken from the 2015/16 Premier League season to train a model to 
accurately predict the xG of a given shot, using features like the distance and angle to 
goal, shot technique, and other shot circumstances.


# Data

This project utilizes statsbomb to pull every shot taken in the 15/16 PL season, which comes
out to ~9,900 shots in total. The data available on statsbomb isn't ready to be fed to a 
model, not without first cleaning and formatting. The features established to be used in 
training are: shot distance/angle (derived from position on the field), shot technique, shot 
type, body part used, and 3 additional boolean flags representing whether the player was 
under pressure, if the shot was a one-on-one with the goalie, and if it was a first time shot.


# Model Approach

This project creates both a Logistic Regression and xgBoost model and uses log loss to determine 
which model performs better. The reason for the multi-model approach is that there are linear 
relationships as well as more complex patterns that correlate shot circumstances with shot outcome. 
Logistic regression can highlight the linear relationships; closer to goal means better chance of 
scoring. xgBoost could pick up on more complex patterns, such as the effectiveness of certain 
shot techniques in different scenarios, like utilizing a chip shot in a one-on-one. 

Both models used the same dataset with a standard 80/20 train-test split. The xgBoost model 
utilized grid-search paired with 5-fold cross-validation to tune the set of hyperparameters and 
find the optimal setup. After training both models, the measured log loss and AUC were as follows:

            |    Log Loss      |     AUC     |
----------------------------------------------
Log. Reg.   |     0.2688       |   0.7773    |
----------------------------------------------
xgBoost     |     0.2668       |   0.7753    |

The results show that both models were extremely similar in performance. In the end, the decision
to use the logistic regression model was simply due to the fact that the xgBoost model 
underperformed based on its complexity and my own expectation of noticeably outperforming the LR model. 
I can only hypothesize that the reason xgBoost underperforms is the lack of complex patterns present
in the data set. xgBoost thrives when it comes to recognizing complex patterns that don't follow a 
linear relationship, and given that the xgBoost model matched the LR model, I can deduce that the
features used in training simply lacked complexity for the xgBoost model to really work its magic.
A future v2 model could use a more diverse feature set, including goalie and defender positions and 
assist metrics, to give the xgBoost model more to work with and allow it to perform better.


# Findings

The model works. After thorough testing, I found the model mostly capable of generating an xG value 
for a user specific shot, and the output value is actually realistic. There isn't a right or wrong 
with xG; different models will give different values, but as long as they align with common knowledge
in the world of football, the values can be accepted. 

One major observation I noticed, while testing how different parameters were affecting the same shot,
was that simply by switching the foot used from left to right, the xG would rise considerably. 
For some shots I tested, that rise was ~0.1, and even for some free kicks that obviously favored 
a left footer, the xG still rose ~0.03 for a right footer. This obvious bias towards right 
footed shots is most likely explained by the inherent bias that exists in the dataset. In the sport, 
a majority of players are right footed, meaning a majority of shots are right footed; any given 
player will obviously prefer shooting on their stronger foot. Even if the shots were split 50/50 
between right and left footers, a significant portion of left footed shots are right footed players 
on their weaker left foot; any given player shooting on their weaker foot is less likely to score 
than with their stronger foot. The class imbalance between right and left footed players leaves the 
model to assume a right footed shot is more likely to go in, purely because more players are right 
footed. That logic is incorrect; a player's strong foot only matters when assessing whether or not 
they used their strong or weak foot, not which specific foot is their stronger. The hypothesized 
solution to this would be adding an additional feature to distinguish strong and weak footed shots.
This way, the model could create more specific categories for right/left footed shots and minimize 
the effect of the bias. 

The more significant observation is the effect of a first time shot on the model. When testing 
different shots on the model, I found that first time shots had a higher xG than normal shots, 
which by football common sense is simply not true; it should be the other way around. The 
explanation for this lies in the fact that all the attempted first time shots are disproportionately
taken in already dangerous situations. A player won't attempt a first time shot unless the 
circumstances make it a viable option, which already implies a higher xG situation. I can hypothesize
that the model interpreted first time shot as meaning a better scoring opportunity, despite the fact 
that it should actually mean a harder shot to score and therefore lower xG. I can only guess this is 
due to a gap in the data when it comes to the circumstances of the shot, like quality of assist. The 
takeaway is that models capture correlation, not causation. The model pieced together a relation 
based on the data, but it is unable to apply logic to these relationships. It can only connect what 
it has in front of it, which leads to purely data driven observations, which can end up ignoring what
is assumed to be common sense. The solution going forward is to provide enough data to cover the gaps
present in the models understanding, in order to balance the weight the model places in each feature 
and prevent the model from relying on a single feature for more than one reason.  


# Next Steps

The model works well to an extent, being that it can give an understandable xG value for most shots.
There are just the few observations made earlier that need to be addressed. The issue of class 
imbalance with left and right footed shots could be fixed by breaking those categories down further,
by adding an additional toggle for strong or weak foot. The problem with this is the data available
through statsbomb doesn't include foot-preference of the player who took the shot. This data could be
gathered through other means, which although tedious may prove beneficial. The other necessary 
addition is features for pass description. As of now, the first time flag is serving as a pass 
descriptor, which is inherently flawed and leaves some unexplainable values produced by the model. 
Additional features to describe the pass to the shot would help ease the weight that the model places
on the first time shot flag, which might allow for its intended effect. 

In additon to those necessary changes, the v2 model needs to be a step up in all aspects, in order to
recognize the more complex patterns that a richer feature set may present. An xgBoost 
model would be the obvious choice, however to optimize its effectiveness, the dataset needs to be 
equally complex and large enough to let the model work its magic. The addition of freeze frame data, 
including goalkeeper and defender positions at the time of the shot, will add to the complexity of 
the dataset. Expanding the dataset to include another full season will double the data available to 
the model; more for the model to learn from. 

With these changes, the v2 model will test the hypothesized solutions to the problems with the 
current model. Any noticeable improvement in logloss/AUC would be a success, but it will be just as 
important to ensure that every single feature is working with its intended effect. The model 
is useless if it doesn't align with common knowledge of the sport. 
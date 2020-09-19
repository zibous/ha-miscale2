# MI Scale 2 Python script

Python script to read values from MI Scale 2. Under testing. Test and report if the script returns correct (or nearly correct) data or not.
Add required details like your MI Scale MAC address, MQTT username, password, host IP address in the code.
You also need to add your height in cm in the code to calculate BMI and other data which depends upon it.
Calculation formulas taken from openScale page. (https://github.com/oliexdev/openScale/)

## Body mass index
Body mass index (BMI) is a value derived from the mass (weight) and height of a person. The BMI is defined as the body mass divided by the square of the body height, and is universally expressed in units of kg/m2, resulting from mass in kilograms and height in metres.
BMI = (weight / height\*height)
https://en.wikipedia.org/wiki/Body_mass_index#BMI_Prime

Category BMI (kg/m2) BMI Prime
from to from to
Very severely underweight 15 0.60
Severely underweight 15 16 0.60 0.64
Underweight 16 18.5 0.64 0.74
Normal (healthy weight) 18.5 25 0.74 1.0
Overweight 25 30 1.0 1.2
Obese Class I (Moderately obese) 30 35 1.2 1.4
Obese Class II (Severely obese) 35 40 1.4 1.6
Obese Class III (Very severely obese) 40 1.6

## Corpulence index
The Corpulence Index (CI) or Ponderal Index (PI) is a measure of leanness (corpulence) of a person calculated as a relationship between mass and height. It was first proposed in 1921 as the "Corpulence measure" by Swiss physician Fritz Rohrer and hence is also known as Rohrer's Index.[4] It is similar to the body mass index, but the mass is normalized with the third power of body height rather than the second power.

CI = weight / height _ height _ height (kg/m)


# Body Cell Mass (BCM)
This is also reported as a percentage of your total weight and as the actual pounds that make up cells that are active like your muscles and organs. The body cell mass are the cells that create your metabolism and energy.   They are what keep you healthy. When the body cell mass goes up, you are usually putting on muscle weight. But, when it goes down, you are losing muscle mass.

# ECM: stands for extracellular mass. 
This number is the amount of your body weight in pounds that is made up of your skeleton and other support structures, as well as ECW.  It is composed of tissue that is between cells.  When this number changes, it is showing that there was a change in the ECW. This number does not show changes in bone density.


# Fat-Free Mass FFM:  
## describes the combination of all cells and tissues that are not fat, in other words, the FatFree Mass.

Impedance Index: is another measurement of your general health. Normal values for both men and women are greater than 1273. If your impedance index is more than 1273, you are at a better level of health and fitness than if it is below 1273.

## Fat-Free Mass
FFM = a * HEIGHT2 + b * WEIGHT + c * AGE + d * R + e 

## Fat-Free Mass in Athletes
FFM = a * HEIGHT2 / R + b * WEIGHT + c

Auto-selection of FFM is performed (see Note 2). 
The equation for elite athletes, based upon Oppliger (5)

FFM (kg) = 0.186 * (HEIGHT*HEIGHT) (cm) / R + 0.701 * WEIGHT (kg) + 1.949 

resistance 	R 	ohms
reactance 	X 	ohms
impedance 	Z 	ohms
phase angle 	α
capacitance 	C

is weighted into the FFM result as follows:

Exercise Hours/Week	Male	Female
0-2	0 %	0 %
3	10	3
4	15	7
5	20	10
6	25	13
7	30	17
8	35	20
9	40	23
10	45	27
11	50	30
12	60	33
13	70	37
14	80	40
15	90	43
16	100	47
17	100	50
18	100	53
19	100	57
20	100	60

(5) Oppliger RA, Nielsen DH, Hoegh JE, and Vance CG, 1991. Bioelectrical impedance prediction of fat-free mass for
    high school wrestlers validated. Medicine and Science in Sports and Exercise, 23, S73. 	
see: https://www.biodyncorp.com/tools/450/parameters.html



## Body fat percentage

Fat: this is reported both as a percentage of your total weight and your actual body weight in pounds that is fat.  Normal values are based on age and gender. Just as you don’t want too much fat, you also want to avoid too little.  Having too little fat can cause your body to stop producing important hormones. For men, this means testosterone.

According to a study published in the British Journal of Nutrition in 1991, if you are an adult, your percentage of body fat can be estimated as accurately as with skin-fold measurements and bioelectrical tests using the following gender-based formulas in conjunction with your BMI. This calculation has been shown to slightly overestimate body fat percentage in people who are very overweight. Take your BMI result from Step 3 and plug it into the appropriate formula below to calculate your body fat percentage.

Women:

- (1.20 x BMI) + (0.23 x Age) - 5.4 = Body Fat Percentage
  Men:
- (1.20 x BMI) + (0.23 x Age) - 16.2 = Body Fat Percentage

As by anthropometric methods, body fat percentage can be estimated from a person's BMI by the following formula:[39]

bodyfatpercentage = 1.39 × BMI + 0.16 × age − 10.34 × gender − 9

where gender (sex) is 0 if female and 1 if male to account for the lower body fat percentage of men.

Body Fat Percentage (BFP)
Body Fat Percent is calculated by dividing the total weight of the fat divided by the body weight. Every human needs to have a certain amount of essential fat. The essential fat percent varies hugely between women and men. Below is a chart of body fat percent ranges for women and men.

BFP Formula For Adults
BFP = (1.20 _ BMI) + (0.23 _ Age) − (10.8 \* S) − 5.4
Where:
S = 1 for male and 0 for female.
BMI = Body Mass Index.
Age = Age in years.

Fat % Category
BFP Category Women Men
Essential Fat Percent 10-13% 2-5%
Fat Percent for Athletes 14-20% 6-13%
Fitness Level 21-24% 14-17%
Average Level 24-31% 18-24%
Obese Level 32% and above 25% and above


Best published equation for the calculation of Body Fat in a sample of Colombian young males using Bioelectrical Impedance Analysis:

Lukaski: (0.756Ht2/R) + (0.110BM) + (0.107Xc) – 5.463
Van Loan and Mayclin: (0.00085Ht2) + (0.3736BM) – (0.02375R) – 0.1531A) +17.7868 (0.00132Ht2) + (0.3052BM) – (0.04394R) – 0.1676A) + 22.66827
Deurenberg: (0.34Ht2/R) + (0.1534Ht) + (0.273 BM) – (0.127 A) + 4.56 (0.476Ht2/R) + (0.295BM) + 5.49 (0.518Ht2/R) + (0.231BM) + (0.130Xc) – (4.229S)
Lohman: (0.476Ht2/R) + (0.295BM) + 5.49
Kyle et al: (0.518Ht2/R) + (0.231BM) + (0.130Xc) – (4.229S)
https://link.springer.com/chapter/10.1007/978-3-540-73841-1_207

All formulae give an estimation of FFM. 
Ht = height in cm, 
R = resistance in Ω, 
BM = body mass = weight in kg, 
Xc = reactance in Ω, 
A = age in years, 
S = sex: men = 1 women = 0.


## Bioelectrical Impedance Analysis: Is It a Reliable Estimator of Lean Body Mass and Total Body Water? 

Multiple regression analysis was used to develop prediction equations for LBM-r and TBW-r, 
with males coded as 0 and females coded as 

LBM-r = 17.7868 + 0.000985*S² (cm) + 0.3736*W (kg) - 0.0238*R (ohm) - 4.2921*SEX - 0.153*AGE (yrs) 
R² = 0.917 SEE = 3.231 Kg 
   
TBW-r = 9.9868 + 0.000723*S² (cm) + 0.2822*W (kg) - 0.0153*R (ohm) - 2.3313*SEX - 0.1319*AGE (yrs) 
R² = 0.871 SEE = 2.919 L

https://www.jstor.org/stable/41463874

RJL:             LBM=wt−(wt*(4.95/(1.1554–0.0841(wt*R)/ht2)−4.5)*100/100)
Lukaski:         LBM=0.734(ht2/R)+0.116(wt)+0.096(Xc)+0.878(Sex:F,0;M,l) −4.03
Segal: <20% BF : LBM=0.00066360(ht2)−0.02117(R)+0.62854(wt)−0.12380(age) +9.33285
       >20% BF : LBM=0.00088850(ht2)−0.02999(R)+0.42688(wt)−0.07002(age) +14.52435  
VanLoan:         LBM=0.00085(ht2)+0.3767(wt)−0.02375(R)−0.1531(age) +17.7868
Deurenberg:      LBM=0.698*102102ht2/R+3.5 (Sex:F.0;M.1 )+9.4

Wt: weight in kg
ht: height in cm 
R : resistance  in ohms
XC: reactance in ohms
BF = body fat.

https://www.researchgate.net/publication/14181755_Assessment_of_total_body_water_and_lean_body_mass_from_anthropometry_Watson_formula_creatinine_kinetics_and_body_electrical_impedance_compared_with_antipyrine_kinetics_in_peritoneal_dialysis_patients/link/02bfe510be9856bb08000000/download

## Body water calculator

Our calculator uses dr. P.E. Watson's formula:

- **For males:**
  `TBW = 2.447 - 0.09156 * age + 0.1074 * height (cm) + 0.3362 * weight (kg)`
- **For females:**
  `TBW = -2.097 + 0.1069 * height (cm) + 0.2466 * weight (kg)`

According to the article, these equations calculate the total body water for adults of any age.

In the past, the Watson Formula was used to calculate total body water. The formula determines the volume of body water based upon gender, height, weight, age, and diabetic status; the calculations involved are different for men and women.

For men: V = 2.447 + 0.3362 x weight (kg) + 0.1074 x height (cm) – 0.09516 x age
For women: V = -2.097 + 0.2466 x weight (kg) + 0.1069 x height (cm)

1. Watson Formula
   TBW-W (for Male) = 2.447 - (0.09156 x A) + (0.1074 x ht) + (0.3362 x wt) litres
   TBW-W (for Female) = -2.097 + (0.1069 x ht) + (0.2466 x wt) litres
   Where:
   A = age in years.
   ht = Height in centimeters(cm).
   wt = Weight in kilograms(kg).

2. Hume-Weyer Formula
   TBW-H (for Male) = (0.194786 x H) + (0.296785 x W) - 14.012934
   TBW-H (for Female) = (0.344547 x H) + (0.183809 x W) - 35.270121
   Where:
   H = Height in centimeters(cm).
   W = Weight in kilograms(kg).

3. Chertow Formula
   TBW-C = H x (0.0186104 x W + 0.12703384) + W x (0.11262857 x M + 0.00104135 x A - 0.00067247 x W - 0.04012056) - A x (0.03486146 x M + 0.07493713) - M x 1.01767992 + D x 0.57894981
   Where:
   A = age in years.
   H = Height in centimeters(cm).
   W = Weight in kilograms(kg).
   M = Male (Yes = 1, No = 0).
   D = Diabetes (Yes = 1, No = 0).

see: https://www.mytecbits.com/tools/medical/total-body-water-calculator#about


## Intracellular Water (ICW)
Intracellular Water (ICW): the fluid inside all of your body’s cells.  The cells of your muscles and organs 
(liver, kidney, brain, etc) contain more water than fat cells.  
The closer to ideal your ICW, the greater the number of cells that contribute to your metabolism.

ICW (liters) = a * HEIGHT2 * X / R2 + b * WEIGHT + c * AGE + d
resistance 	R 	ohms
reactance 	X 	ohms
impedance 	Z 	ohms
phase angle 	α
capacitance 	C
 
## Total Body Water (TBW)
If you are dehydrated or losing a lot of fluid, your total body water may be low. 
If you are retaining fluid or have an infection, your total body water may be elevated compared to ideal.

TBW (liters) = a * HEIGHT2 / R + b * WEIGHT + c * AGE + d
resistance 	R 	ohms
reactance 	X 	ohms
impedance 	Z 	ohms
phase angle 	α
capacitance 	C

TBW = (Height*Height)/Impedance

Impedance = (Height*Height) / TBW

Verteilung des TBW
Extrazellulär: 43  %  des   TBW    (Lymphe, interstitiell, transzellulär, Plasma)
Intrazellulär: 57  %  des   TBW

## LBW Equation woman
Lean Body Weight (LBW in kg) = (0.65 \* height in cm) - 50.74

### LBW Equation men
Lean Body Weight (LBW in kg) = (0.65 \* height in cm) - 59.42



Lean body mass (LBM) is a part of body composition that is defined as the difference between total body weight and body fat weight. This means that it counts the mass of all organs except body fat, including bones, muscles, blood, skin, and everything else. While the percentage of LBM is usually not computed, it on average ranges between 60-90% of total body weight. Generally, men have a higher proportion of LBM than women do. The dosages of some anesthetic agents, particularly water-soluble drugs, are routinely based on the LBM. Some medical exams also use the LBM values. For body fitness and routine daily life, people normally care more about body fat percentage than LBM. To compute body fat, consider using our [body fat calculator](https://www.calculator.net/body-fat-calculator.html) or [ideal weight calculator](https://www.calculator.net/ideal-weight-calculator.html).

Multiple formulas have been developed for calculating estimated LBM (eLBM) and the calculator above provides the results for all of them.

### Lean Body Mass Formula for Adults

**The Boer Formula:**
For men: LBM = (0.407 × W) + (0.267 × H) − 19.2
For women: LBM = (0.252 × W) + (0.473 × H) − 48.3
where W is body weight in kilograms and H is body height in centimeters.

**The James Formula:**2

| _For males:_            |
| ----------------------- |
| eLBM = 1.1W - 128(WH)2  |
| _For females:_          |
| eLBM = 1.07W - 148(WH)2 |

**The Hume Formula:**3
For men: LBM = (0.32810 × W) + (0.33929 × H) − 29.5336
For women: LBM = (0.29569 × W) + (0.41813 × H) − 43.2933
where W is body weight in kilograms and H is body height in centimeters.

## Mathematical Formulas to Calculate FFMI

### Total Body Fat Formula

- **Metric:** Total Body Fat = Weight in Kg \* (body fat % / 100)
- **English:** Total Body Fat = Weight in lb \* (body fat % / 100)

### Lean Body Weight Formula

- **Metric:** Lean Weight = Weight in Kg \* (1 - (body fat % / 100)
- **English:** Lean Weight = Weight in lb \* (1 - (body fat % / 100)

### FFMI Formula

- **Metric:** FFMI = (Lean Weight in Kg / 2.2) \* 2.20462 / ((meters) 2
- **English:** FFMI = (Lean Weight in lb / 2.2) / ((Feet _ 12.0 + Inches) _ 0.0254)2

### Adjusted FFMI Formula

- **Metric:** Adjusted FFMI = FFMI + ( 6.1 \* (1.8 - (meters))
- **English:** Adjusted FFMI = FFMI + ( 6.1 _ (1.8 - (Feet _ 12.0 + Inches) \* 0.0254))

# Ideal Body Weight

### Basic Background Information

For simplicity sake, we use the following formulas, but there are a number of different formulas used to calculate ideal body weight.

- **MEN: IBW (kgs) = 22 x (height in meters)2**
- **WOMEN: IBW (kgs) = 22 x (height in meters - 10cm)2**

A person is considered obese if they weigh 30% above their ideal body weight.

The World Health Organization (WHO) recommends both men and women to keep [their BMI](https://www.calculators.org/health/bmi.php) between 18.5 to 25.

Adjusted body weight is used for drug dosing measurements.

Adjusted body weight = IBW + 0.4 \* ( actual weight - IBW)

### Additional Formulas

G. J. Hamwi's Formula from 1964

- **men:** 48.0 kg + 2.7 kg per inch over 5 feet
- **women:** 45.5 kg + 2.2 kg per inch over 5 feet

B. J. Devine's Formula from 1974

- **men:** 50.0 kg + 2.3 kg per inch over 5 feet
- **women:** 45.5 kg + 2.3 kg per inch over 5 feet

J. D. Robinson's Formula from 1983

- **men:** 52 kg + 1.9 kg per inch over 5 feet
- **women:** 49 kg + 1.7 kg per inch over 5 feet

D. R. Miller's Formula from 1983

- **men:** 56.2 kg + 1.41 kg per inch over 5 feet
- **women:** 53.1 kg + 1.36 kg per inch over 5 feet



# Basal metabolic rate (BMR) 
Is the amount of energy the body burns to accomplish basic life functions. This includes breathing, blood circulation, cell production, and nutrient absorption.
Basal Metabolic Rate (BMR) is how many calories are burned at rest during the average day. The metabolic rate is determined by how many cells are producing oxidative energy.  
The more cells, the more energy, and the higher the basal metabolic rate.  Thyroid, other hormones, medications, etc. all can affect the basal metabolic rate.  
A low basal metabolic rate means that any calories you consume above your unique basal metabolic rate are 
unnecessary to supporting you and will be converted into storage (fat).  A low body temperature would occur if your rate of calorie burn is too low.   
If you consume a lot more calories than you need, then you may have an excessive appetite problem, which can be due to a neurotransmitter imbalance.

**The Harris-Benedict BMR formula:**

**Men:** BMR = 66 + (6.2 × weight in pounds) + (12.7 × height in inches) – (6.76 × age in years)
**Women:** BMR = 655.1 + (4.35 × weight in pounds) + (4.7 × height in inches) – (4.7 × age in years)

For a faster way to get your BMR, use the above calculator.

Look at the example below to see how it's done.

- Age: 30
- Gender: Female
- Height: 62 inches
- Weight: 115.3 lbs.

**BMR** = 655.1 + (4.35 × weight in pounds) + (4.7 × height in inches) – (4.7 × age in years)

= 655.1 + (4.35 x 115.3 lbs.) + (4.7 x 62 inches) – (4.7 x 30)
= 655.1 + 501.555 + 291.4 – (141)
= 1,448.055 – 141
BMR = 1,307.055

### Calculating the Harris–Benedict BMR

Men: BMR = 66.5 + ( 13.75 × weight in kg ) + ( 5.003 × height in cm ) – ( 6.755 × age in years
Woman: = 655 + ( 9.563 × weight in kg ) + ( 1.850 × height in cm ) – ( 4.676 × age in years )

### The Harris–Benedict equations revised by Roza and Shizgal in 1984

Men BMR = 88.362 + (13.397 × weight in kg) + (4.799 × height in cm) - (5.677 × age in years)
Women BMR = 447.593 + (9.247 × weight in kg) + (3.098 × height in cm) - (4.330 × age in years)

### The Harris–Benedict equations revised by Mifflin and St Jeor in 1990:

Men BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) + 5
Women BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) - 161

Determine Total Energy Expenditure
Lifestyle Example PAL Calculation
Sedentary or light activity Office worker getting little or no exercise 1.53
BMR x 1.53
Active or moderately active Construction worker or person running one hour daily 1.76
BMR x 1.76
Vigorously active Agricultural worker (non mechanized) or person swimming two hours daily 2.25 BMR x 2.25

### Calculate Your Total Daily Energy Expenditure (TDEE)

**TDEE = BMR x Activity Level**

| Activity Level    | Number | Description                                                                                        |
| :---------------- | :----- | :------------------------------------------------------------------------------------------------- |
| Sedentary         | 1.2    | People who work desk jobs and engage in very little exercise or chores.                            |
| Lightly active    | 1.375  | People who do chores and go on long walks/engage in exercise at least 1 to 3 days in a week.       |
| Moderately active | 1.55   | People who move a lot during the day and workout (moderate effort) at least 3 to 5 days in a week. |
| Very active       | 1.725  | People who play sports or engage in vigorous exercise on most days.                                |
| Extra active      | 1.9    | People who do intense workouts 6 to 7 days a week with work that demands physical activity.        |

# Data folder

The data of the calculations are saved here.

## miscale- {USER} .json
Is used to calculate the history (see calcdata .__ calcdatadiff __ ()).

```python
...
if data_prev:
    result = dict()
    result['user'] = self.user
    result['weight'] = round(self.data['weight'] - data_prev['weight'], 2)
    result['fat'] = round(self.data['fat'] - data_prev['fat'], 2)
    result['water'] = round(self.data['water'] - data_prev['water'], 2)
    result['muscle'] = round(self.data['muscle'] - data_prev['muscle'], 2)
    result['visceral'] = round(self.data['visceral'] - data_prev['visceral'], 2)
    result['protein'] = round(self.data['protein'] - data_prev['protein'], 2)
    return result
....
```

## YYYY-M-{USER}.csv
Log data of the measurements per month and user.


All other files are used for the test cases and are not managed by the application.
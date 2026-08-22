# What I checked, and what the agent got wrong

## What the agent got wrong

Bob's first fix for the missing `last_service_km` key set the default to `SERVICE_INTERVAL_KM` (15000). That was wrong. For VOS-7788 with `odometer=92000`, it produced `92000 - 15000 = 77000 km since service` — 513% worn — so the car was still falsely flagged. I caught this because I ran the tests after the fix and one test was still red. The correct default is the car's own odometer value, so `km_since = 0`, meaning "treat a missing record as just serviced." After that correction all four tests went green.

## What I checked before I accepted its work

I ran `pytest` after every fix and watched the count go from 3 failing to 0. I then ran `python verify.py` and tracked the score climb from 9/11 to 10/11. I also reviewed the helper-module audit before any fixes were applied — that's how I confirmed the `MILES_PER_KM = 1.609` bug was real (it is the km-to-miles ratio inverted, so the nightly UK report was printing about 2.6x the true fleet distance). I checked that the 15000 km interval and 80% threshold were untouched in both `km_wachter.py` and `settings.cfg` before accepting.

## What the data actually said

The two columns that actually separate cars that broke down from cars that did not are `km_since_service` (+61% mean gap) and `avg_daily_km` (+22% gap). The "obvious" answers — total mileage and age — turned out to be noise: `odometer_km` had a +0.3% gap and `age_years` had a -0.2% gap, both meaningless. The quartile breakdown rates made this clearest: cars in the highest `km_since_service` quartile broke down at a 56.7% rate versus 3.3% for recently-serviced cars — a 17x difference. The risk score built from those two columns put 8 of the 10 actual breakdown cars in the top 10, compared with roughly 2 expected from a random draw.

# workhours
Register work hours in cli.

Stamp in before starting the workday, tag points in time with comments and stamp out when workday is over.

Hours are saved to a sqlite database and exportable to pdf.


# Usage

### Start worktime
##### With current time
`./stamp.py add`
##### With modified time
`./stamp.py add -D 2013-03-03 -T 21:00`


### End worktime
##### With current time
`./stamp.py end`
##### With modified time
`./stamp.py end -D 2013-03-03 -T 21:00`


### Tag a point in time
##### With current time
`./stamp.py tag 'My message for the tag'`
##### With modified time
`./stamp.py tag 'My message for the tag' -D 2013-03-03 -T 21:00`


### Get status of registered and current hours
##### Get status of all registered hours
`./stamp.py status`
##### Get status with filter
Not perfected yet


### Export to pdf
`./stamp.py export`
Works but is not perfected


### Delete workday or tags
##### Delete workday
`./stamp.py 15`
##### Delete tag under workday
`./stamp.py 15 --tag 3`


### Edit registered or current hours
##### Edit registered hours
`./stamp.py edit --id 15 'company="My second customer",date="2015-02-02"'`
##### Edit current hours (just remove the id argument)
`./stamp.py edit 'company="My second customer",date="2015-02-02"'`
##### It is also possible to explicitly declare current hours
`./stamp.py edit --id 'current' 'company="My second customer",date="2015-02-02"'`


### Edit tags
##### Edit registered tag
`./stamp.py edit --id 15 -t 1 'comment="This is my tag",date="2015-02-02"'`
##### Edit tag under current workday (just remove the id argument)
`./stamp.py edit -t 1 'comment="This is my tag",date="2015-02-02"'`


## Functionality to add
- [ ] Make filter work properly with status using the same options as editing.
- [ ] Trigger mail to customers with pdf invoice.
- [ ] Add an boolean option to mark for paid or not paid.
- [ ] Config file.
- [ ] Add to linux distribution package managers starting with Arch Linux.
- [ ] Connect to git.

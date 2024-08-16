The git contains facebook scraper tbat takes web link to the group and fetches post messages with the link to them.
    NOTE*   For a proper work of scraper the RUSSIAN LAY OUT is required.


********    FOR TELEGRAM INTERFACE PART    ********

- Group links have to be inserted into table named "input" into "group_links" column

- The scraper returns post messages and links to the posts in one row.
- All the posts that are ready to be sent to the client have column named "to_send" which is supposed to take values 0 or 1.
- To fetch all info that is ready to be sent use "to_send" column where it will be equal to 1.

- After sending the post info to the user DO NOT FORGET to change the value of "to_send" to 0.

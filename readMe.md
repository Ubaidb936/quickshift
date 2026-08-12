we need to build a two sided market place where a bussiness registers and post the shift that the workers can fill.

Bussiness:
    id
    1- Name
    2- location
    3- working hours
    etc

shift:
   id
   1- position
   2- working hours(start time to end time)
   3- pay rate per hour
   4- Duities
   5- attire
   6- number of workers

worker
  id
  name
  location
  profession
  etc

match
  id
  bussiness_id
  worker_id
  shift_id

There is a registor for bussiness and workers usuallly signup

login is same? and routes to pages accordingly different for a user.

bussiness have a dashboard to post a shift.

// bussines router
  / register enpoint
  / login endpoint
  / signout endpoint
  / what jwt for authetication?

   

//shifts router
 / post_shift endpoint
 / get_shifts endpoint
 / delete_shift
 / pause_shift
 / edit shift

// matches
  / get_interested
  / accept worker
  / decline worker


worker has main page

/ shifts around based on the locations and profession match

/ show_interest

/ not available for a match

logins

file structure for backend

     backend fast api
          app folder
           api folder 
               authentication.py
               shifts.py
               matches.py
               
           database folder
               connect to sql database
           other services folders
           
           utis folder
              schema.py
              config.py

           core.py   cors and routers registered here
           auth.py
          main.py uvicorn run command

    frontend react and javascript
         pages
         components
         scss
         app.js for routes
         services
           api.js
           auth.js
           
    Dockerfile



        
              







  



  












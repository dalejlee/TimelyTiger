<!DOCTYPE html>
<html>
   <head>
      <title>Timely Tiger</title>

      <meta name="viewport" content="width=device-width,
        initial-scale=1">
   </head>
   <body onLoad="OnLoadBody();">
      <div style="width:90%;margin-left:50px;margin-right: 50px;margin-top: 50px;">
         <table style="width:100%">
            <tr>
               <td>
                  <img src="/static/KidTigerArtistFL.png" width="130px" height="100px" alt="tiger">
               </td>
               <td>
                  <img src="/static/NewEventButton.png" width="218px" height="100px" alt="new event" onclick="CreateNewEvent()">
               </td>
               <td align="left">
                  <font face="Comic Sans MS", size="7">
                  Timely Tiger
                  </font>
                  <br>
                  <font face="Comic Sans MS", size="2">
                  Version {{TTVersionNumber}}
                  </font>
               </td>
               <td align="right">
                  <div id='LoginUser'>
                     <img src="{{loginPersonPhotoLink}}" href="/authorize" width="50px" height="50px" alt="User Photo">
                     <br><font style="font-size:12px">{{LoginPersonName}}</font>
                     <A style="font-size:8px" href="javascript:UpdateUserDateEdit('{{LoginPersonEmail}}','{{LoginPersonName}}','{{loginPersonPhotoLink}}');">edit</A>
                  </div>
                  <div ID=EditUser style="visibility: hidden; display:none;">
                     <table style='width: 90%;'>
                        <tr style='font-size:small;'>
                           <td align=left style='width: 100%'>
                              Display name
                              <input type="Name" id="EditUserName" value='{{LoginPersonName}}' style='width: 100%;'/>
                              <br><br>Display photo URL
                              <input type="button" onclick="ClearUserPhotoLink()" value='Clear'>
                              <input type="Photo Link" id="EditUserPhotoLink" value='{{loginPersonPhotoLink}}' style='width: 100%;'>
                           </td>
                           <tr>
                              <td align=right >
                                 <input type="button" onclick="UpdateUserDateSave('{{LoginPersonEmail}}')" value='save'>
                                 <input type="button" onclick="UpdateUserDateClose()" value='close'>
                              </td>
                           </tr>
                        </tr>
                     </table>
                  </div>
                  <input type="hidden" id="UserEmail" name="UserEmail" value="{{LoginPersonEmail}}">
                  <A style="font-size:12px" href="/authorize">Sign out</A>
               </td>
            </tr>
         </table>
         <table ID="AllEvents" style="width:100%;border-collapse:collapse;">
         </table>
      </div>
      <script src="https://apis.google.com/js/platform.js" async defer></script>
      <meta name="google-signin-client_id" content="899885585030-j4o4conctbnpmke5qqjekejufeo8lb70.apps.googleusercontent.com">
      <script>
         function ClearUserPhotoLink()
         {
            document.getElementById("EditUserPhotoLink").value="";
         }
         function addUserEmail()
         {
            var UserEmail = document.getElementById("UserEmail").value;
            return '&UserEmail='+UserEmail;
         }
         function OnLoadBody()
         {
            RefreshAllEvents();
         }
         function UpdateUserDateClose()
         {
            var EditUserDIV = document.getElementById("EditUser");
            EditUserDIV.style.visibility='hidden';
            EditUserDIV.style.display='none';           
         }
         function UpdateUserDateSave(email)
         {
            var EditUserDIV = document.getElementById("EditUser");
            EditUserDIV.style.visibility='hidden';
            EditUserDIV.style.display='none';


            request = createAjaxRequest();
            if (request == null) return;

            var EditUserName = document.getElementById("EditUserName").value;
            var EditUserPhotoLink = document.getElementById("EditUserPhotoLink").value;

            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/UpdateUserData?messageId=" + messageId + "&Email=" + email + "&Name=" + EditUserName + "&PhotoLink=" + EditUserPhotoLink + addUserEmail();

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);
         }
         function UpdateUserDateEdit(email,name,photoHTML)
         {
            var EditUserDIV = document.getElementById("EditUser");
            EditUserDIV.style.visibility='visible';
            EditUserDIV.style.display='inline';
         }
         function signOut() 
         {
            try
            {
               var auth2 = gapi.auth2.getAuthInstance();
               auth2.signOut;
               alert("signed out");
            }
            catch(err) {
               alert(err);
            }           
         } 
         function createAjaxRequest()  // From Nixon book
         {
            var req;
                       
            try  // Some browser other than Internet Explorer
            {
               req = new XMLHttpRequest();
            }
            catch (e1) 
            {    
               try  // Internet Explorer 6+
               {
                  req = new ActiveXObject("Msxml2.XMLHTTP");
               }
               catch (e2) 
               {  
                  try  // Internet Explorer 5
                  { 
                     req = new ActiveXObject("Microsoft.XMLHTTP"); 
                  }
                  catch (e3)
                  {  
                     req = false;
                  }
               }
            }
            return req;
         }

         function processReadyStateChange()
         {
            var STATE_UNINITIALIZED = 0;
            var STATE_LOADING       = 1;
            var STATE_LOADED        = 2;
            var STATE_INTERACTIVE   = 3;
            var STATE_COMPLETED     = 4;
            
            if (this.readyState != STATE_COMPLETED)
               return;
            
            if (this.status != 200)  // Request succeeded?
            {  
               //alert(
               //   "AJAX error: Request failed: " + this.statusText);
               return;
            }
            
            if (this.responseText == null)  // Data received?
            {  
               alert("AJAX error: No data received");
               return;
            }

            // Extract the TigerEventNumber and the HTML data
            var FullString = this.responseText;
            var DOMid=FullString.substring(0,FullString.indexOf(","));
            var HTMLPortion=FullString.substring(FullString.indexOf(",")+1,FullString.length);

            // Force user to login, if commanded
            if (DOMid=='ForceAuthorization')
            {
               alert("Sorry, you are already logged into Timely Tiger with a different account in this browser. We are logging out this account.");
               window.location = "/authorize";
            }

            // Update specific object
            var AllEventsTable = document.getElementById(DOMid);
            AllEventsTable.innerHTML = HTMLPortion;
         }

         // Keep this around for debuging
         // alert("GOT HERE");
         //    return;

         var seed = date.getSeconds();
         var request = null;

         var ID=0;   // Might use this to close if a user opens a new event without saving an old
         function ScheduleEvent(TigerEventID)
         {
            request = createAjaxRequest();
            if (request == null) return;

            if(document.getElementById("SelectedTime"+TigerEventID)==null)
            {
               alert("Must have a meeting time to be sheduled")
               return; 
            }


            // Get the entered parameters to send back to server
            var EventTitle = document.getElementById("EventTitle"+ TigerEventID).value;
            var EventDescription = document.getElementById("EventDescription"+TigerEventID).value;
            var EventLength = document.getElementById("EventLength"+TigerEventID).value;
            var EventLocation = document.getElementById("EventLocation"+TigerEventID).value;

            // Check response lengths
            if(EventTitle.length > 100)
            {
               alert("title must be under 100 characters")
               return;
            }
            if(EventDescription.length > 1000)
            {
               alert("Description must be under 1000 characters")
               return;
            }
            if(EventLocation.length > 1000)
            {
               alert("Location must be under 1000 characters")
               return;
            }

            // Check for characters that will screw up the database or HTML
            if(      EventLocation.indexOf("#")>-1 
                  || EventLocation.indexOf("<")>-1 
                  || EventLocation.indexOf(">")>-1 
                  || EventLocation.indexOf("&")>-1 
                  || EventLocation.indexOf("*")>-1
                  || EventLocation.indexOf("'")>-1
                  )
            {
               alert("Characters #, >, <, &, * or ' are not allowed in the Location field");
               return;               
            }
            if(      EventDescription.indexOf("#")>-1 
                  || EventDescription.indexOf("<")>-1 
                  || EventDescription.indexOf(">")>-1 
                  || EventDescription.indexOf("&")>-1 
                  || EventDescription.indexOf("*")>-1
                  || EventDescription.indexOf("'")>-1
                  )
            {
               alert("Characters #, >, <, &, * or ' are not allowed in the event description field");
               return;               
            }
            if(      EventTitle.indexOf("#")>-1 
                  || EventTitle.indexOf("<")>-1 
                  || EventTitle.indexOf(">")>-1  
                  || EventTitle.indexOf("&")>-1 
                  || EventTitle.indexOf("*")>-1
                  || EventTitle.indexOf("'")>-1
                  )
            {
               alert("Characters #, >, <, &, * or ' are not allowed in the event title field");
               return;               
            }


            // getting timezone
            // var curdate = new Date();
            // var dOffset = curdate.getTimezoneOffset();
            // console.log(dOffset);

            // Construct our request and send
            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/ScheduleEvent?messageId=" + messageId + "&TigerEventID=" + TigerEventID + "&EventTitle=" + EventTitle + "&EventDescription=" + EventDescription + "&EventLength=" + EventLength + "&EventLocation=" + EventLocation + addTimeZone() + addUserEmail();

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);
         }
         function SaveEvent(TigerEventID)
         {
            request = createAjaxRequest();
            if (request == null) return;

            // Get the entered parameters to send back to server
            var EventTitle = document.getElementById("EventTitle"+ TigerEventID).value;
            var EventDescription = document.getElementById("EventDescription"+TigerEventID).value;
            var EventLength = document.getElementById("EventLength"+TigerEventID).value;
            var EventLocation = document.getElementById("EventLocation"+TigerEventID).value;

            // Check response lengths
            if(EventTitle.length > 100)
            {
               alert("title must be under 100 characters")
               return;
            }
            if(EventDescription.length > 1000)
            {
               alert("Description must be under 1000 characters")
               return;
            }
            if(EventLocation.length > 1000)
            {
               alert("Location must be under 1000 characters")
               return;
            }

            // Check for characters that will screw up the database or HTML
            if(      EventLocation.indexOf("#")>-1 
                  || EventLocation.indexOf("<")>-1 
                  || EventLocation.indexOf(">")>-1 
                  || EventLocation.indexOf("&")>-1 
                  || EventLocation.indexOf("*")>-1
                  || EventLocation.indexOf("'")>-1
                  )
            {
               alert("Characters #, >, <, &, * or ' are not allowed in the Location field");
               return;               
            }
            if(      EventDescription.indexOf("#")>-1 
                  || EventDescription.indexOf("<")>-1 
                  || EventDescription.indexOf(">")>-1 
                  || EventDescription.indexOf("&")>-1 
                  || EventDescription.indexOf("*")>-1
                  || EventDescription.indexOf("'")>-1 
                  )
            {
               alert("Characters #, >, <, &, * or ' are not allowed in the event description field");
               return;               
            }
            if(      EventTitle.indexOf("#")>-1 
                  || EventTitle.indexOf("<")>-1 
                  || EventTitle.indexOf(">")>-1 
                  || EventTitle.indexOf("&")>-1 
                  || EventTitle.indexOf("*")>-1
                  || EventTitle.indexOf("'")>-1
                  )
            {
               alert("Characters #, >, <, &, * or ' are not allowed in the event title field");
               return;               
            }

            // Construct our request and send
            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/SaveEvent?messageId=" + messageId + "&TigerEventID=" + TigerEventID + "&EventTitle=" + EventTitle + "&EventDescription=" + EventDescription + "&EventLength=" + EventLength + "&EventLocation=" + EventLocation  + addTimeZone() + addUserEmail();

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);

            //var ID = "TigerEvent" + TigerEventID
            //var EventRowToEdit = document.getElementById(ID);
            //RowString ="<td>Peoples pics go here</td><td>TimelyTiger requirments event number " + TigerEventID + "<button onclick='EditEvent(" + TigerEventID + ")'>edit</button></td><td>2 hours</td><td>Dec 17, 2018, 8PM</td><td>Repeat<br>Cancel</td>";
            //EventRowToEdit.innerHTML = RowString;
         }   
         function DeleteEvent(TigerEventID)
         {
            request = createAjaxRequest();
            if (request == null) return;

            // Construct our request and send
            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/DeleteEvent?messageId=" + messageId + "&TigerEventID=" + TigerEventID + addTimeZone() + addUserEmail();

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);
         }
         function SetTigerRefreshTimer(TigerEventID)
         {
            // Refresh this event in about 20 seconds.
            // creat variability based upon event id so that
            // all events don't refresh at the same time
            mseconds=40000+(TigerEventID-100)*1000
            setTimeout(function(){RefreshEvent(TigerEventID);}, mseconds)       
         }
         function RefreshEvent(TigerEventID)
         {
            // Check for a DOM object that is present only in event detail model...
            var EventAttendeesObject = document.getElementById("EventAttendees"+ TigerEventID);
            if(EventAttendeesObject)
            {
               // This is event is in detail model. So, cause a refresh of only attendees.
               // When attendees refresh, a new timer event will be created by loading an attendee picture

               //var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
               //var url = "/RefreshAttendees?messageId=" + messageId + "&TigerEventID=" + TigerEventID;
               var url = "/RefreshAttendeesDetailView?TigerEventID=" + TigerEventID + addUserEmail();
               request.onreadystatechange = processReadyStateChange;
               request.open("GET", url);
               request.send(null);
            }
            else
            {
               // No EventAttendees control, the event must be in summary mode. 
               // Refresh the whole event (CloseEVent causes a refresh). A new timer
               // event will be created when attendee picture is loaded
               request = createAjaxRequest();
               if (request == null) return;

               // Construct our request and send
               var url = "/RefreshEventSummaryView?TigerEventID=" + TigerEventID + addTimeZone() + addUserEmail();
               request.onreadystatechange = processReadyStateChange;
               request.open("GET", url);
               request.send(null);
            }
         }
         function CloseEvent(TigerEventID)
         {
            request = createAjaxRequest();
            if (request == null) return;

            // Construct our request and send
            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/CloseEvent?messageId=" + messageId + "&TigerEventID=" + TigerEventID + addTimeZone() + addUserEmail();

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);
         } 
         function UnscheduleEvent(TigerEventID)
         {
            request = createAjaxRequest();
            if (request == null) return;

            // Construct our request and send
            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/UnscheduleEvent?messageId=" + messageId + "&TigerEventID=" + TigerEventID + addTimeZone() + addUserEmail();

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);
         } 
               
         function EditEvent(TigerEventID)
         {
            // Abort any pending requests
            if (request != null)
               request.abort();

            // Create a new Ajax request
            request = createAjaxRequest();
            if (request == null) return;

            // Construct our request and send
            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/EditEvent?messageId=" + messageId + "&TigerEventID=" + TigerEventID + addTimeZone() + addUserEmail();

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);

            //ID = "TigerEvent" + TigerEventID;
            //var EventRowToEdit = document.getElementById(ID);
            //EventRowToEdit.innerHTML = "<td colspan=5><br><br>Hey! Here is event data to edit <button onclick='SaveEvent("+TigerEventID+")'>save</button><br><br></td>";
         }
         
         function CreateNewEvent()
         {
            // Abort any pending requests
            //if (request != null)
            //   request.abort();

            // Create a new Ajax request
            request = createAjaxRequest();
            if (request == null) return;
            
            // Construct our request and send
            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/CreateNewEvent?messageId=" + messageId  + addTimeZone() + addUserEmail();

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);

            //ID = "TigerEvent" + TigerEventID;
            //var EventRowToEdit = document.getElementById(ID);
            //EventRowToEdit.innerHTML = "<td colspan=5><br><br>Hey! Here is event data to edit <button onclick='SaveEvent("+TigerEventID+")'>save</button><br><br></td>";
         }
         function RefreshAllEvents()
         {            
            // Abort any pending requests
            //if (request != null)
            //   request.abort();

            // Create a new Ajax request
            request = createAjaxRequest();
            if (request == null) return;

            // Construct our request and send
            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/RefreshAllEvents?messageId=" + messageId + addTimeZone() + addUserEmail();

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);
         }
         function DeleteAttendee(TigerEventID,attendeeEmail)
         {
            // Abort any pending requests
            //if (request != null)
            //   request.abort();

            // Create a new Ajax request
            request = createAjaxRequest();
            if (request == null) return;

            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/DeleteAttendee?messageId=" + messageId + "&TigerEventID=" + TigerEventID + "&AttendeeEmail=" + attendeeEmail  + addUserEmail();

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);

            GetSuggestedTimes(TigerEventID);
         }
         function ValidateEmail(mail) 
         {
            if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(mail))
            {
               return (true)
            }
            alert("Nonconforming email")
            return (false)
         }
         function AddAttendee(TigerEventID)
         {
            // Create a new Ajax request
            request = createAjaxRequest();
            if (request == null) return;

            var NewAttendeeEmail = document.getElementById("NewAttendeeEmail"+TigerEventID).value;

            // if clicking with no entry, do nothing
            if(NewAttendeeEmail.length=="")
               return;

            if(!ValidateEmail(NewAttendeeEmail))
               return;

            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/AddAttendee?messageId=" + messageId + "&TigerEventID=" + TigerEventID + "&NewAttendeeEmail=" + NewAttendeeEmail  + addUserEmail();

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);

            GetSuggestedTimes(TigerEventID);

         }
         function addTimeZone()
         {
            // getting timezone
            var curdate = new Date();
            var dOffset = curdate.getTimezoneOffset();

            return "&tz=" + dOffset;
         }
         function GetSuggestedTimes(TigerEventID)
         {
            request = createAjaxRequest();
            if (request == null) return;

            var contrlRangeStart = document.getElementById("RangeStart"+TigerEventID);
            var BeginDateTime=contrlRangeStart.value;

            var contrlRangeEnd = document.getElementById("RangeEnd"+TigerEventID);
            var EndDateTime=contrlRangeEnd.value;

            var contrlEventLength = document.getElementById("EventLength"+TigerEventID);
            var EventLength = contrlEventLength.value;

            // // getting timezone
            // var curdate = new Date();
            // var dOffset = curdate.getTimezoneOffset();
            // console.log(dOffset);
            // document.getElementById('tz').value = dOffset;

            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/GetSuggestedTimes?messageId=" + messageId 
                     + "&TigerEventID=" + TigerEventID 
                     + "&BeginDateTime=" + BeginDateTime 
                     + "&EndDateTime=" + EndDateTime 
                     + "&EventLength=" + EventLength
                     + addTimeZone() + addUserEmail();

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);


            //alert("got to end of GetSuggestedTimes: " + url);
         }
         function SubmitSelectedTime(TigerEventID)
         {
            // Send the selected time, selected amoung suggested times
            // back to server. Server will return HTML that shows only selected

            request = createAjaxRequest();
            if (request == null) return;

 
            // Determine which time was selected...

            var SuggestedTimesForm = document.getElementById("SuggestedTimesForm"+TigerEventID);
            var NumRadios = SuggestedTimesForm.length
            //alert("number of radios:" + NumRadios)
            var SelectedTime=-1;
            for(var i=0; i<NumRadios;i++)
            {
               if(SuggestedTimesForm[i].checked)
               {
                  //alert(SuggestedTimesForm[i].value);
                  SelectedTime=SuggestedTimesForm[i].value;
                  break;
               }
            }

            // User did not make a selection. Do nothing and let them
            // figure out what is wrong.
            if (SelectedTime==-1) return;

           // Send back other elements also...

            var contrlRangeStart = document.getElementById("RangeStart"+TigerEventID);
            var BeginDateTime=contrlRangeStart.value;

            var contrlRangeEnd = document.getElementById("RangeEnd"+TigerEventID);
            var EndDateTime=contrlRangeEnd.value;

            var contrlEventLength = document.getElementById("EventLength"+TigerEventID);
            var EventLength = contrlEventLength.value;


            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/SubmittSelectedTime?messageId=" + messageId 
                     + "&TigerEventID=" + TigerEventID 
                     + "&SelectedTime=" + SelectedTime
                     + "&BeginDateTime=" + BeginDateTime
                     + "&EndDateTime=" + EndDateTime 
                     + "&EventLength=" + EventLength
                     + addTimeZone() + addUserEmail();

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);
         }
      </script>
   </body>
</html>
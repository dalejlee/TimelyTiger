<!DOCTYPE html>
<html>
   <head>
      <title>Timely Tiger</title>

      <meta name="viewport" content="width=device-width,
        initial-scale=1">
   </head>
   <body onLoad="OnLoadBody();">
      <div style="width:100%px;margin-left:10px;margin-right: 10px;margin-top: 10px;">
         <table style="width:100%">
            <tr>
               <td>
                  <img src="/static/KidTigerArtistFL.png" width="78px" height="60px" alt="tiger">
                  <img src="/static/NewEventButton.png" width="131px" height="60px" alt="new event" onclick="CreateNewEvent()">
               </td>
               <td align="left">
                  <font face="Comic Sans MS", size="6">
                  Timely Tiger
                  </font>
                  <br>
                  <font face="Comic Sans MS", size="2">
                  Version {{TTVersionNumber}}, mobile, {{LoginPersonName}} <A style="font-size:12px" href="/authorize">Sign out</A>
                  </font>
               </td>
            </tr>
         </table>
         <table ID="AllEvents" style="width:100%;border-collapse:collapse;">
         </table>
      </div>
      <script src="https://apis.google.com/js/platform.js" async defer></script>
      <meta name="google-signin-client_id" content="899885585030-j4o4conctbnpmke5qqjekejufeo8lb70.apps.googleusercontent.com">
      <script>
         function OnLoadBody()
         {
            // setTimeout(function(){ alert("Hello 1"); }, 3000);
            // setTimeout(function(){ alert("Hello 2"); }, 6000);
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
            var url = "/UpdateUserData?messageId=" + messageId + "&Email=" + email + "&Name=" + EditUserName + "&PhotoLink=" + EditUserPhotoLink;

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

            // getting timezone
            // var curdate = new Date();
            // var dOffset = curdate.getTimezoneOffset();
            // console.log(dOffset);

            // Construct our request and send
            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/ScheduleEvent?messageId=" + messageId + "&TigerEventID=" + TigerEventID + "&EventTitle=" + EventTitle + "&EventDescription=" + EventDescription + "&EventLength=" + EventLength + "&EventLocation=" + EventLocation + addTimeZone();

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);
         }
         function DeleteEvent(TigerEventID)
         {
            request = createAjaxRequest();
            if (request == null) return;

            // Construct our request and send
            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/DeleteEvent?messageId=" + messageId + "&TigerEventID=" + TigerEventID + addTimeZone();;

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
               var url = "/RefreshAttendeesDetailView?TigerEventID=" + TigerEventID;
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
               var url = "/RefreshEventSummaryView?TigerEventID=" + TigerEventID + addTimeZone();
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
            var url = "/CloseEvent?messageId=" + messageId + "&TigerEventID=" + TigerEventID + addTimeZone();

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
            var url = "/UnscheduleEvent?messageId=" + messageId + "&TigerEventID=" + TigerEventID + addTimeZone();

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

            // Construct our request and send
            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/SaveEvent?messageId=" + messageId + "&TigerEventID=" + TigerEventID + "&EventTitle=" + EventTitle + "&EventDescription=" + EventDescription + "&EventLength=" + EventLength + "&EventLocation=" + EventLocation  + addTimeZone();

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);

            //var ID = "TigerEvent" + TigerEventID
            //var EventRowToEdit = document.getElementById(ID);
            //RowString ="<td>Peoples pics go here</td><td>TimelyTiger requirments event number " + TigerEventID + "<button onclick='EditEvent(" + TigerEventID + ")'>edit</button></td><td>2 hours</td><td>Dec 17, 2018, 8PM</td><td>Repeat<br>Cancel</td>";
            //EventRowToEdit.innerHTML = RowString;
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
            var url = "/EditEvent?messageId=" + messageId + "&TigerEventID=" + TigerEventID + addTimeZone();

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
            var url = "/CreateNewEvent?messageId=" + messageId + addTimeZone();

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
            var url = "/RefreshAllEvents?messageId=" + messageId + addTimeZone();

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
            var url = "/DeleteAttendee?messageId=" + messageId + "&TigerEventID=" + TigerEventID + "&AttendeeEmail=" + attendeeEmail ;

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);

            GetSuggestedTimes(TigerEventID);
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

            var messageId = Math.floor(Math.random(seed) * 1000000) + 1;
            var url = "/AddAttendee?messageId=" + messageId + "&TigerEventID=" + TigerEventID + "&NewAttendeeEmail=" + NewAttendeeEmail ;

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
                     + addTimeZone();

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
                     + addTimeZone();

            request.onreadystatechange = processReadyStateChange;
            request.open("GET", url);
            request.send(null);
         }
      </script>
   </body>
</html>
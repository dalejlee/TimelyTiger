<h2>Create an Event</h2>
<hr>
<form action="showTimes" method="get">
			<table>
				<tr>
					<td>Event Title:</td>
					<td>
						<input type="text" name ="eventName" value="{{eventName}}">
						<br>
					</td>
				</tr>
				<tr>
					<td>Your Email:</td>
					<td>
						<input type="email" name ="yEmail" value="{{yEmail}}">
						<br>
					</td>
				</tr>
				<tr>
					<td>Partner's Email:</td>
					<td>
						<input type="email" name ="pEmail" value="{{pEmail}}">
						<br>
					</td>
				</tr>
				<tr>
					<td>Meeting length (in minutes):</td>
					<td>
						<input type="number" name ="meetingLength" value="{{meetingLength}}">
						<br>
					</td>
				</tr>
				<tr>
					<td>Start Time Range:</td>
					<td>
						<input type="date" name ="startdate" value="{{startdate}}">
						<br>
					</td>
				</tr>
				<tr>
					<td>End Time Range::</td>
					<td>
						<input type="date" name ="enddate" value="{{enddate}}">
						<br>
					</td>
				</tr>
				<tr>
					<td>Place:</td>
					<td>
						<input type="text" name ="place" value="{{place}}">
						<br>
					</td>
				</tr>
				<tr>
					<td></td>
					<td>
						<input type="submit" value="Create Event">
					</td>
				</tr>
			</table>	
		</form>
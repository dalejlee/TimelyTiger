<h2>Create an Event</h2>
<hr>
<form action="showTimes" method="get">
			<table>
				<tr>
					<td>Your Email:</td>
					<td>
						<input type="text" name ="yEmail" value="{{prevyEmail}}">
						<br>
					</td>
				</tr>
				<tr>
					<td>Partner's Email:</td>
					<td>
						<input type="text" name ="pEmail" value="{{prevpEmail}}">
						<br>
					</td>
				</tr>
				<tr>
					<td>Date (MMDDYYYY):</td>
					<td>
						<input type="text" name ="date" value="{{prevDate}}">
						<br>
					</td>
				</tr>
				<tr>
					<td>Time (in hours):</td>
					<td>
						<input type="text" name ="time" value="{{prevTime}}">
						<br>
					</td>
				</tr>
				<tr>
					<td>Place:</td>
					<td>
						<input type="text" name ="place" value="{{prevPlace}}">
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
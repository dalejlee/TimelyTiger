<h2>Create an Event</h2>
<hr>
<form action="showTimes" method="get">
			<table>
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
					<td>Date:</td>
					<td>
						<input type="date" name ="date" value="{{date}}">
						<br>
					</td>
				</tr>
				<tr>
					<td>Time (in hours):</td>
					<td>
						<input type="number" name ="time" min="1" max="24" value="{{time}}">
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
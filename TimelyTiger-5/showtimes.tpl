There are {{num_times}} times that fit your criteria. <br>
Please select one.

<ul>
	% for time in times:
		<li><a href="eventDetails?time={{time}}"> {{time}}</a></li>
	% end
</ul>
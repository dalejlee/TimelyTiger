You have created {{num_events}} events. <br>
Click to view details.

<ul>
	% for event in events:
		<li><a href="pastEventDetails?eventid={{event[1]}}"> {{event[0]}}</a></li>
	% end
</ul>
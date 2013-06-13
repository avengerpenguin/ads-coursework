xquery version "3.0";
for $programme in //programme
where $programme/availability/window/start_time < current-dateTime()
  and $programme/availability/window/end_time > current-dateTime()
return $programme

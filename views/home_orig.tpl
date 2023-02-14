<!doctype html>

<html>
	<head>
		<style>
body {
    color: #555;
    font-family: sans-serif;
    padding: 0 1em 1em 1em;
}

a {
    font-family: sans-serif;
}

td {
    font-family: Verdana, Geneva, sans-serif;
    font-size: 10pt;
    color: #828282;
}
td.crap {
    font-family: Verdana, Geneva, sans-serif;
    font-size: 10pt;
    color: #aaa;
}
.story {
    line-height: 2em;
}
.story.crap {
    line-height: 0.75em;
}
.story.crap a {
    color: #aaa;
    font-size: 0.75em;
}
.paren {
  color: #c9c9c9 !important;
}
.paren:first-child {
  margin-left: 5px;
}
		</style>
	</head>

	<body>
		<h1>HN</h1>

		<table>
		%for _, storyd in good_stories.items():
            %story = list(storyd.values())[0] 
            <tr>
            <td><a href="{{ story['comments_link'] }}" target="_blank">{{ story['comments_num'] }}</a></td>
            <td><span class="score hot" title="Points">{{ story['points'] }}</span></td>
            <td class="title">
                <a href="{{ story['link'] }}" class="storylink" target="_blank">{{ story['title'] }}</a>
                <span class="sitebit comhead">
                    <span class="paren">(</span><span>{{ story['host'] }}</span><span class="paren">)</span>
                </span>
            </td>
            </tr>
		%end
		</table>

		<h1>HN crap</h1>

		<table>
		%for _, storyd in crap_stories.items():
            %story = list(storyd.values())[0] 
            <tr class="crap">
            <td class="crap"><a href="{{ story['comments_link'] }}" target="_blank">{{ story['comments_num'] }}</a></td>
            <td class="crap"><span class="score hot" title="Points">{{ story['points'] }}</span></td>
            <td  class="crap">
                <a href="{{ story['link'] }}" class="storylink" target="_blank">{{ story['title'] }}</a>
                <span class="sitebit comhead">
                    <span class="paren">(</span><span>{{ story['host'] }}</span><span class="paren">)</span>
                </span>
                <span class="sitebit comhead">
                    <span class="paren">(</span><span>{{ storyd['why'] }}</span><span class="paren">)</span>
                </span>
            </td>
            </tr>
		%end
		</table>
	</body>
</html>


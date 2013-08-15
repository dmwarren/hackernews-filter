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
		</style>
	</head>

	<body>
		<h1>HN</h1>

		<ul>
		%for i in range(0, len(good_stories)):
			%story = good_stories[i]
			<li class="story">
				<a href="{{ story['link'] }}">
					{{ story['title'] }}
				</a>
			</li>
		%end
		</ul>

		<ul>
		%for i in range(0, len(crap_stories)):
			%story = crap_stories[i]
			<p class="story crap">
				<a href="{{ story['link'] }}">
					{{ story['title'] }}
				</a>
			</p>
		%end
		</ul>
	</body>
</html>


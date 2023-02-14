<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Filtered HN</title>

    <link href="css/bootstrap.min.css" rel="stylesheet">
    <link href="css/style.css" rel="stylesheet">

  </head>
  <body bgcolor="#202020">

    <div class="container-fluid">
	<div class="row">
		<h1>HN filtered</h1>
		<div class="col-md-9">
			<table class="table table-striped table-hover table-sm">
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
		</div>
	</div>
	<div class="row">
		<h1 data-toggle="collapse" data-target="#crap">HN crap</h1>
		<div class="col-md-9 collapse" id="crap">
			<table class="table table-striped table-hover table-sm">
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
		</div>
	</div>
</div>

    <script src="js/jquery.min.js"></script>
    <script src="js/bootstrap.min.js"></script>
    <script src="js/scripts.js"></script>
  </body>
</html>

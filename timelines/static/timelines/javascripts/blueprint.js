function drawHeader(){
	Pablo.g({class: 'header', height: (rowHeight * headerSizeInRows), width: rowWidth})
		//.append(Pablo.rect({x: 0, y: 0, width: rowWidth, height: rowHeight, fill: '#EEE', 'fill-opacity': .9}))
		//.append(Pablo.rapidsms({x: 25, y: 10, scale: .55, rapidFill: '#FFFFFF', smsFill: '#FFFFFF'}))
		.append(Pablo.text({class: 'header-tagline', x: 20, y: (rowHeight / 2) + 10, width: rowWidth, height: rowHeight, fill: '#000'})
			.attr('style', 'font-size: ' + (2 * scale) + 'em;')
			.content(headerDescription))
		.append(Pablo.rect({x: 0, y: rowHeight, width: rowWidth, height: (rowHeight * headerSizeInRows) - rowHeight, fill: '#FFF', 'fill-opacity': .1}))
		.appendTo(paper);
}


function drawRows(){
	// svg elements and icons for each actor
	for (var i=0, a=actorNames.length; i<a; i++){
		drawRow(actorNames[i], i);
	};
	//Pablo(actorNames).each(drawRow);
}


function drawRow(actorName, i){
	var row = Pablo.g({class: actorName + '-row row', width: paperWidth, height: rowHeight});
	var rowRect = Pablo.rect({class: 'rowRect', x: 0, y: 0, width: paperWidth, height: rowHeight, fill: 'none'})
	row.append(rowRect);

	var actor = Pablo.g({class: actorName + '-container container'})
	var icon = Pablo[actorNames[i]]({scale: scale, x: 5, y: 10})
		.appendTo(actor);
	actor.appendTo(row);

	// grab fill color
	var color = icon.attr('fill');
	if (color === null){
		// no fill color? probably a group of paths, so check the first child
		color = icon[0].childNodes[0].getAttribute('fill');
	};
	var actorLabel = drawRowLabel(actorName, color)
		.appendTo(actor);

	if (i <= 1){
		// first two actors are timeline rows
		var timeline = drawTimelineRow(i, color)
			.appendTo(row);
		timeline.transform('translate', timelineXOffset + ' ' + timelineYOffset)
			//.animateTransform({from: '-1000, 100', to: timelineXOffset + ' ' + timelineYOffset, dur: '500ms', attributeName: 'transform', type: 'translate'});
	} else {
		// remaining actors are touchpoint rows
		var touchpointRowGroups = drawTouchpointRow(actorName, color);
		row.append(touchpointRowGroups);
		if (actorName === 'phone'){
			// final actor is component row
			var componentGroups = drawComponents(color);
			row.append(componentGroups);
		}
	}
	// add rows to paper BEFORE wordWrap calls in bringTimelineLabelsToFront
	row.appendTo(rows);
	rows.appendTo(paper);

	if (i <= 1){
		// wrap text in timeline rows and bring to front
		bringTimelineLabelsToFront(actorName, timeline);
	}
	// slide each row down by a factor of rowHeight
	row.transform('translate', '0 ' + (rowHeight * i))
		//.animateTransform({from: '0, -200', to: '0 ' + (rowHeight * i), dur: '500ms', attributeName: 'transform', type: 'translate'});
}


function drawRowLabel(actorName, color){
	var labelText = actorName;
	if (actorName === 'phone'){
		labelText = 'services';
	}
	var actorLabel = Pablo.text({class: actorName + '-label actor-label', x: rowHeight, y: (rowHeight/2)})
		.attr('style', 'font-size: ' + (.9 * scale) + 'em;')
		.content(labelText)
		.attr('fill', color)
		.transform('translate', (-25 * scale) + ' 0');
	return actorLabel
}


function drawTimelineRow(i, color){
	var actorName = actorNames[i];
	// create timelines for mother and child rows
	var timeline = Pablo.g({class: actorName + '-timeline timeline'});
	timeline.attr({x: rowHeight, y: (rowHeight * i)});

	// prepend light chevrons to mother and child timelines
	Pablo.chevron({scale: scale, x: (-.02 * rowWidth), shape: 'narrow'})
		.attr('fill', lightestShadeOf[color])
		.appendTo(timeline);
	Pablo.chevron({scale: scale, x: (-.011 * rowWidth)})
		.attr('fill', lighterShadeOf[color])
		.appendTo(timeline);

	// keep track of previous element's right-most x position
	var previousX = 0;
	for (var j=0, l=timelineData.length; j<l; j++){
		for (var key in timelineData[j]){
			if (timelineData[j][key][actorName] !== undefined){
				var milestone = timelineData[j][key][actorName];
				var x = (offset + previousX);
				var width = (key - previousX) > minWidth ? (key - previousX) : minWidth;
				var arrow = Pablo.arrow({scale: scale, fill: color, x: x, width: width, text: milestone, textColor: '#000000'})
					.appendTo(timeline);
					//.animateTransform({from: 1000, to: x, attributeName: 'transform', type: 'translate', dur: '500ms'});
				previousX = parseInt(x + width);
			}
		}
	}
	// append light chevrons to mother and child timelines
	Pablo.chevron({scale: scale, x: (previousX + offset)})
		.attr('fill', lighterShadeOf[color])
		.appendTo(timeline);
	Pablo.chevron({scale: scale, x: (previousX + (13.5 * scale) + offset), shape: 'narrow'})
		.attr('fill', lightestShadeOf[color])
		.appendTo(timeline);
	return timeline;
}


function bringTimelineLabelsToFront(actorName, timeline){
	// wrap timeline labels for mother and child rows
	var labelSelector = selector + ' .' + actorName + '-timeline .icon-label';
	Pablo(labelSelector).each(function (d,e){
			wordWrap(d, e);
			// until elem.moveToFront() is available, do it manually
			// https://github.com/dharmafly/pablo/issues/10
			// d.remove() doesnt work in safari.. but
			// copying the remove source from pablo does.. WTF
			// However, Pablo(d).remove() does work in safari.
			// TODO is it better to wrap d with Pablo or just
			// use the vanilla js
			var parentNode = d.parentNode;
			if (parentNode){
					parentNode.removeChild(d);
					timeline.append(d);
			}
			timeline.append(d);
	});
}


function drawTouchpointRow(actorName, color){
	// add touchpoints to non-mother and non-child rows
	// TODO what if there are touchpoints for mother?
	var groups = [];
	for (var j=0, l=touchpoints.length; j<l; j++){
		for (var key in touchpoints[j]){
			if (touchpoints[j][key][actorName] !== undefined){
				var touchpoint = touchpoints[j][key][actorName];
				var x = (scale * key);
				var height = (rowHeight / 3.3333);
				var group = Pablo.g({id: 'touchpoint-' + (j + 1), class: actorName + '-touchpoint touchpoint'})

				if (touchpoints[j][key]['point-type'] !== undefined){
					if (touchpoints[j][key]['point-type'] === 'optional'){
						group.append(Pablo.rect({fill: color, x: x, y:height,  width: 9, height: 9}));

						Pablo.text({'font-family': 'SilkscreenNormal', x: x, y: (height + 10), width: 20, height: 20})
							.attr('text-rendering', 'optimizeLegibility')
							.attr('style', 'font-size: ' + (.8 * scale) + 'em;')
							.attr('fill', '#888888')
							.attr('class', 'touchpoint-label touchpoint-label-optional')
							.content(touchpoint)
							.transform('rotate', '-25 ' + (x - 5) + ' ' + (height - 25))
							.appendTo(group);
					}
				} else {
					group.append(Pablo.circle({fill: color, cx: x, cy:height,  r: 5}));

					Pablo.text({'font-family': 'SilkscreenNormal', x: x, y: (height + 10), width: 20, height: 20})
						.attr('text-rendering', 'optimizeLegibility')
						.attr('style', 'font-size: ' + (.8 * scale) + 'em;')
						.attr('fill', color)
						.attr('class', 'touchpoint-label')
						.content(touchpoint)
						.transform('rotate', '-25 ' + (x - 20) + ' ' + (height - 15))
						.appendTo(group);
				}
				group.transform('translate', timelineXOffset + ' ' + timelineYOffset);
				groups.push(group);
			}
		}
	}
	return groups;
}


function drawComponents(color){
	var groups = []
	var maxComponents = 0;
	// sort components by magnitude (widest segment first)
	serviceComponents.sort(compareMagnitudes);
	for (var m=0, n=serviceComponents.length; m<n; m++){
		maxComponents = Math.max(maxComponents, serviceComponents[m]['components'].length);
		if (m > 0) {
			if (segmentContainsPoint(serviceComponents[m-1]['start'], serviceComponents[m-1]['stop'], serviceComponents[m]['start'])
					|| segmentContainsPoint(serviceComponents[m-1]['start'], serviceComponents[m-1]['stop'], serviceComponents[m]['stop'])) {
				// if this segment intersects previous segment,
				// increase maxComponents
				maxComponents += 1;
				// and flag this segment for a new row
				serviceComponents[m]['newRow'] = true;
			}
		}
	}
	var thisRow = 0;
	for (var m=0, n=serviceComponents.length; m<n; m++){
		var pointer = 0;
		if (serviceComponents[m]['newRow']){
			thisRow += 1;
		}
		for (var s=0, t=serviceComponents[m]['components'].length; s<t; s++){
			var x = (offset * scale * 12) + (serviceComponents[m]['start'] * scale) + pointer;
			var y = (((offset + 30) * scale) * (thisRow + s + 1));
			var width = (scale * serviceComponents[m]['stop']) - x;
			var group = Pablo.g({class: 'service-component'});

			// add white rect so marker lines will not be visible
			group.append(Pablo.rect({fill: '#FFFFFF', x: x, y: y,  width: width, height: (scale * 25)}));
			group.append(Pablo.rect({fill: color, 'fill-opacity': .25, x: x, y: y,  width: width, height: (scale * 25)}));

			var words = serviceComponents[m]['components'][s].split(' ');
			var label = Pablo.text({x: x, y: y, width: 20, height: 20})
					.attr('class', 'service-component-label');

			do {
				var word = words.pop();
				var wordX = x + ((offset + 2) * scale);
				var wordY = y + 6 + (words.length * (6 * scale));
				Pablo.tspan({'font-family': 'SilkscreenNormal', x: wordX, y: wordY, class: 'service-component-label-tspan'})
					.attr('style', 'font-size: ' + (.8 * scale) + 'em;')
					.attr('fill', color)
					.content(word)
					.appendTo(label);
			} while (words.length);

			label.appendTo(group);
			group.transform('translate', timelineXOffset + ' ' + ((-(scale * offset * 30) * (maxComponents - 1))));
			groups.push(group);
		}
		pointer = (x + width);
	}
	return groups;
}


function drawTouchpoints(){
	var points = '';
	for (var j=0, l=touchpoints.length; j<l; j++){
		Pablo(selector + ' #touchpoint-' + (j+1)).each(function(d,i){
			// determine which row includes this touchpoint
			var thisRow;
			var actorName;
			if (d.hasOwnProperty('classList')){
				actorName = d.classList[0].split('-')[0];
			} else {
				actorName = d.className.baseVal.split(' ')[0].split('-')[0];
			}
			for (var k=0, m=actorNames.length; k<m; k++){
				if (actorNames[k] === actorName){
					thisRow = k;
					break;
				}
			}
			// find position of touchpoint, add offsets
			var thisX;
			var thisY;
			if (typeof(d.firstChild["cx"]) !== 'undefined'){
				thisX = timelineXOffset + (d.firstChild.getAttribute("cx") * 1);
			} else {
				// add 4.5 so line is centered on rect
				thisX = 4.5 + timelineXOffset + (d.firstChild.getAttribute("x") * 1);
			}
			if (typeof(d.firstChild["cy"]) !== 'undefined'){
				thisY = (rowHeight * thisRow) + timelineYOffset + (d.firstChild.getAttribute("cy") * 1);
			} else {
				// add 4.5 so line is centered on rect
				thisY = 4.5 + (rowHeight * thisRow) + timelineYOffset + (d.firstChild.getAttribute("y") * 1);
			}
			// add coordinates to string of points
			points += thisX + ',' + thisY + ' ';
		})
	};
	var line = drawTouchpointsLine(points);
	//line.animateTransform({from: '0, -400', to: '0, 0', dur: '500ms', attributeName: 'transform', type: 'translate'});
	line.appendTo(rows);
}


function drawTouchpointsLine(points){
	// draw line connecting touchpoints in order
	return Pablo.polyline({points: points, fill: 'none'})
		.attr('stroke', '#92278F')
		.attr('stroke-width', 4)
		.attr('stroke-miterlimit', 10)
		.attr('stroke-linejoin','round')
		.attr('stroke-linecap','round')
		.attr('stroke-opacity', 0.33)
}


function drawBlueprint(paperSelector, height, actors, components, blueprintTouchpoints, description){
	// TODO maybe move all these globals into window.config or similar
	window.selector = paperSelector;
	window.actorNames = actors;
	window.serviceComponents = components;
	window.touchpoints = blueprintTouchpoints;
	window.headerDescription = description;

	window.lighterShadeOf = {"#39B54A": "#D0E8CA", "#00AEEF": "#B9E5FB"}
	window.lightestShadeOf = {"#39B54A": "#EAF4E7", "#00AEEF": "#E1F4FD"}

	// golden ratio FTW
	var golden = ((1 + Math.sqrt(5)) / 2);
	window.paperHeight = height;
	window.paperWidth = paperHeight * golden;
	window.paper =  Pablo(selector).root({width: paperWidth, height: paperHeight});

	window.scale = (.00075 * paperWidth);
	console.log('scale: ' + scale);

	window.headerSizeInRows = 1.5;
	window.rowHeight = (paperHeight / (actorNames.length + headerSizeInRows));
	console.log('rowHeight: ' + rowHeight);
	// make small elements big enough to hold labels
	window.minWidth = (rowHeight / 2);

	window.rowWidth = paperWidth;

	window.timelineXOffset = rowHeight * 1.5;
	console.log('timelineXOffset: ' + timelineXOffset);

	window.timelineYOffsetFactor = 5;
	window.timelineYOffset = rowHeight / timelineYOffsetFactor;
	console.log('timelineYOffset: ' + timelineYOffset);

	// add a little space between elements
	window.offset = (paperWidth * .0005);

	window.rows = Pablo.g({class: 'rows'});

	drawHeader();
	var columns= drawColumns();
	rows.append(columns);
	drawRows();
	drawTouchpoints();
	rows.transform('translate', '0 ' + (rowHeight * headerSizeInRows));
}


function drawColumns(){
	var columns = Pablo.g({class: 'columns'});
	var months = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33];
	var markerPositions = months.map(function(i){ return i * 30.4375});
	var markerLabels = months.map(function(i){ return i - 9});
	for (var i=0, l=months.length; i<l; i++){
		var column = Pablo.g({class: 'column column-' + months[i]});
		var x = (((offset * (i+1)) * scale) + ((markerPositions[i] + 12)* scale));
		// stop short of bottom of paper so lines don't extend beyond components
		var y = (paperHeight - (1.75 * rowHeight));

		var line = Pablo.line({x1: x, y1: -5, x2: x, y2: y})
			.attr('stroke', '#CCC')
			.attr('stroke-width', '1px')
			.attr('opacity', '.9')
			.appendTo(column);

		var label = Pablo.text({'font-family': 'SilkscreenNormal', x: x, y: 0})
			.attr('style', 'font-size: ' + (.8 * scale) + 'em;')
			.append(Pablo.tspan().content(markerLabels[i]))
			.appendTo(column);

		if ((i + 1) == months.length){
			label.append(Pablo.tspan().content(' months'));
		}
		if (i % 2 == false){
			label.attr('fill', '#AAA')
		}
		//column.animateTransform({from: '-1000, 0', to: '0, 0', dur: '500ms', attributeName: 'transform', type: 'translate'});
		columns.append(column);
	}
	columns.transform('translate', timelineXOffset + ' -' + (timelineYOffset))
	return columns;
}


function wordWrap(d){
	var textWidth = d.getBBox().width;
	var parentWidth = d.parentNode.getBBox().width;
	if ((parentWidth - minWidth) < textWidth){
		var words = d.textContent.split(' ');
		var longestWordLength = Math.max.apply(Math, words.map(function (el) { return el.length }));
		var line = new Array();
		var word;
		var x = d.getAttribute("x");
		var y = d.getAttribute("y");
		// clear element's textContent
		d.textContent = '';
		// adjust vertical position based on how many lines will be used
		Pablo(d).transform('translate', '0 ' + ((words.length - 1) * (6 * scale)));
		do {
			word = words.shift();
			line.push(word);
			var wordX = x;
			var wordY = y - (words.length * (10 * scale));
			// wrap each word in a tspan
			Pablo.tspan({'font-family': 'SilkscreenNormal', x: wordX, y: wordY, class: 'icon-label-tspan'})
				.content(word)
				.appendTo(d);
		} while (words.length);
	}
}


function compareMagnitudes(a, b) {
	var aMag = (a['stop'] - a['start']);
	var bMag = (b['stop'] - b['start']);
	if (aMag < bMag)
		return 1;
	if (aMag > bMag)
		return -1;
	return 0;
}


function segmentContainsPoint(segStart, segStop, point){
	if ((point > segStart) && (point < segStop)){
		return true;
	}
	return false;
}

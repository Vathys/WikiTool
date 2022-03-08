function magnify(imgID, zoom) {
  var img, glass, w, h, bw;
  img = document.getElementById(imgID);

  /* Create magnifier glass: */
  glass = document.createElement("DIV");
  glass.setAttribute("class", "img-magnifier-glass");

  /* Insert magnifier glass: */
  img.parentElement.insertBefore(glass, img);

  /* Set background properties for the magnifier glass: */
  glass.style.backgroundImage = "url('" + img.src + "')";
  glass.style.backgroundRepeat = "no-repeat";
  glass.style.backgroundSize = (img.width * zoom) + "px " + (img.height * zoom) + "px";
  bw = 3;
  w = glass.offsetWidth / 2;
  h = glass.offsetHeight / 2;
  glass.style.display = "none";

  /* Execute a function when someone moves the magnifier glass over the image: */
  glass.addEventListener("mousemove", moveMagnifier);
  img.addEventListener("mousemove", moveMagnifier);

  /*and also for touch screens:*/
  glass.addEventListener("touchmove", moveMagnifier);
  img.addEventListener("touchmove", moveMagnifier);
  function moveMagnifier(e) {
    var pos, x, y;
    /* Prevent any other actions that may occur when moving over the image */
    e.preventDefault();
    /* Get the cursor's x and y positions: */
    pos = getCursorPos(e);
    x = pos.x;
    y = pos.y;
    
    var x_lower = w / zoom;
    var x_upper = img.width - x_lower;
    
    var y_lower = h / zoom;
    var y_upper = img.height - y_lower;
    
    /* Prevent the magnifier glass from being positioned outside the image: */
    
    if(x > x_upper || x < x_lower || y > y_upper || y < y_lower) {
      glass.style.display = "none";
    } else {
      glass.style.display = "block";
	 glass.style.backgroundImage = "url('" + img.src + "')";
	 glass.style.backgroundRepeat = "no-repeat";
	 glass.style.backgroundSize = (img.width * zoom) + "px " + (img.height * zoom) + "px";
    }
    if (x > img.width - (w / zoom)) {
      x = img.width - (w / zoom);
    }
    if (x < w / zoom) {
      x = w / zoom;
    }
    if (y > img.height - (h / zoom)) {
      y = img.height - (h / zoom);
    }
    if (y < h / zoom) {
      y = h / zoom;
    }
    /* Set the position of the magnifier glass: */
    glass.style.left = (x - w + img.offsetLeft) + "px";
    glass.style.top = (y - h + img.offsetTop) + "px";
    /* Display what the magnifier glass "sees": */
    glass.style.backgroundPosition = "-" + ((x * zoom) - w + bw) + "px -" + ((y * zoom) - h + bw) + "px";
  }

  function getCursorPos(e) {
    var a, x = 0, y = 0;
    e = e || window.event;
    /* Get the x and y positions of the image: */
    a = img.getBoundingClientRect();
    /* Calculate the cursor's x and y coordinates, relative to the image: */
    x = e.pageX - a.left;
    y = e.pageY - a.top;
    /* Consider any page scrolling: */
    x = x - window.pageXOffset;
    y = y - window.pageYOffset;
    return {x : x, y : y};
  }
}

function showContent() {
	this.classList.toggle("active");
	var content = this.nextElementSibling;
	if (content.style.display === "block") {
		content.style.display = "none";
	} else {
		content.style.display = "block";
	}
}

function insertTOCButton() {
	const targets = document.getElementsByClassName('toc');
	for(let i = 0; i < targets.length; i++) {
		var target = targets[i];
		var h1 = target.getElementsByTagName('h1')[0];
		
		const button = document.createElement('button');
	
		button.setAttribute("type", "button");
		button.setAttribute("class", "collapsible");
		
		h1.remove();
		
		button.appendChild(h1);
		
		target.parentNode.insertBefore(button, target);
	}
}

function openNav() {
	document.getElementsByClassName('openbtn')[0].style.display = "none";
	document.getElementsByClassName("sidebar")[0].style.transform = "scaleX(1)";
	//document.getElementsByClassName("container")[0].style.marginLeft = "16%";
}

function closeNav() {
	document.getElementsByClassName("openbtn")[0].style.display = "inline-block";
	document.getElementsByClassName("sidebar")[0].style.transform = "scaleX(0)";
	//document.getElementsByClassName("container")[0].style.marginLeft = "0";
}

function expandlist() {
	let list = this.parentElement.parentElement.getElementsByClassName('dropdown-content')[0];
	let isDown = !(list.style.display === "block");
	this.innerHTML = isDown ? "&#11165;" : "&#11167";
	list.style.display = isDown ? "none" : "block"
	if(list.style.display === "block"){
		list.style.display = "none";
	} else {
		list.style.display = "block";
	}
}

function buildNavChildren(object, target) {
	let list = document.createElement('ul');
	list.classList.add('dropdown-content');
	
	for(let i = 0; i < object.children.length; i++){
		let child = object.children[i];
		let item = document.createElement('li');
		
		let lidiv = document.createElement('div');
		lidiv.classList.add('dropdown');
		
		let link = document.createElement('a');
		link.href = child.href;
		link.innerText = child.label.replaceAll("_", " ");
		if(document.location.pathname.slice(1) === child.href){
			link.classList.toggle("active");
		}
		
		let downarrow = document.createElement('button');
		downarrow.classList.add('expand');
		downarrow.innerHTML = "&#11167;";
		downarrow.addEventListener("click", expandlist);
		
		if(child.hasOwnProperty('children')){
			lidiv.appendChild(downarrow);
		} else {
			downarrow.setAttribute('disabled', 'disabled');
			if(document.location.pathname.slice(1) === child.href){
				downarrow.classList.toggle("active");
			}
			lidiv.appendChild(downarrow);
		}
		lidiv.appendChild(link);
		
		item.appendChild(lidiv);
		
		if(child.hasOwnProperty('children')){
			buildNavChildren(child, item);
		}
		
		list.appendChild(item);
	}
	
	target.appendChild(list);
}

function buildNav() {
	var mv = JSON.parse(data)
	
	var nav_element = document.getElementsByTagName('nav')[0];
	
	var openbtn = document.createElement('button');
	openbtn.classList.add('openbtn');
	openbtn.setAttribute('onclick', 'openNav()');
	openbtn.innerHTML = "&#9776;"
	
	nav_element.appendChild(openbtn);
	
	let div = document.createElement('div');
	div.classList.add('sidebar')
	
	let closebtn = document.createElement('a');
	closebtn.href = "javascript:void(0)";
	closebtn.classList.add('closebtn');
	closebtn.setAttribute('onclick', 'closeNav()');
	closebtn.innerHTML = "&times;";
	
	div.appendChild(closebtn);
	
	let list = document.createElement('ul');
	
	for(let i = 0; i < mv.children.length; i++){
		let child = mv.children[i];
		let item = document.createElement('li');
		
		let lidiv = document.createElement('div');
		lidiv.classList.add('dropdown');
		
		let link = document.createElement('a');
		link.href = child.href;
		link.innerText = child.label.replaceAll("_", " ");
		if(document.location.pathname.slice(1) === child.href){
			link.classList.toggle("active");
		}
		
		let downarrow = document.createElement('button');
		downarrow.classList.add('expand');
		downarrow.innerHTML = "&#11167;";
		downarrow.addEventListener("click", expandlist);
		
		if(child.hasOwnProperty('children')){
			lidiv.appendChild(downarrow);
		} else {
			downarrow.setAttribute('disabled', 'disabled');
			if(document.location.pathname.slice(1) === child.href){
				downarrow.classList.toggle("active");
			}
			lidiv.appendChild(downarrow);
		}
		
		lidiv.appendChild(link);
		
		item.appendChild(lidiv);
		
		if(child.hasOwnProperty('children')){
			buildNavChildren(child, item);
		}
		
		list.appendChild(item);
	}
	
	div.appendChild(list);
	nav_element.appendChild(div);
}
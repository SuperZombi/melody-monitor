window.onload = async _=>{
	updateTheme()
	await buildSettings()
	document.querySelectorAll('[title]').forEach(el => new bootstrap.Tooltip(el))
}

function updateTheme() {
	const colorMode = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
	document.querySelector("html").setAttribute("data-bs-theme", colorMode);
}

async function saveSettings(){
	let els = document.querySelectorAll("#main .row .input-group")
	els.forEach(async el=>{
		let input = el.children[0];
		let value = input.value
		if (input.type == "number"){
			value = input.valueAsNumber
		}
		await eel.update_setting(input.name, value)
	})
	await eel.save_settings()
}


async function buildSettings(){
	let settings = await eel.get_settings()();
	let parent = document.querySelector("#main")
	settings.forEach(s=>{
		let el = Setting(s)
		parent.appendChild(el)
	})
}

function Setting(data){
	let div = document.createElement("div")
	div.className = "row"
	div.innerHTML = `
		<label class="col-sm-4 col-form-label">${data.label}</label>
		<div class="col">
			<div class="input-group"></div>
		</div>
	`
	let input_area = div.querySelector(".input-group")

	if (data.values){
		input_area.innerHTML = `
			<select class="form-select">
				${data.values.map(v=>`<option value="${v.name}">${v.label}</option>`).join('')}
			</select>
		`
	}
	else if (data.type == "str"){
		input_area.innerHTML = `
			<input type="text" class="form-control">
		`
	}
	else if (data.type == "int"){
		input_area.innerHTML = `
			<input type="number" class="form-control" ${data.min ? `min="${data.min}"` : ''}>
		`
	}

	let input = input_area.children[0]
	input.name = data.name
	if (data.dft_value){
		input.placeholder = data.dft_value
	}
	if (data.value){
		input.value = data.value
	}

	if (data.promt){
		let span = document.createElement("span")
		span.className = "input-group-text help"
		span.title = data.promt
		span.innerHTML = `<i class="bi bi-question-circle"></i>`
		input_area.appendChild(span)
	}

	return div
}

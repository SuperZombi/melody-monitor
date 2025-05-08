window.onload = async _=>{
	updateTheme()
	await buildSettings()
	await buildMods()
	document.querySelectorAll('[title]').forEach(el => new bootstrap.Tooltip(el))
}

function updateTheme() {
	const colorMode = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
	document.querySelector("html").setAttribute("data-bs-theme", colorMode);
}

async function saveSettings(){
	let els = document.querySelectorAll("#main .row .input-group")
	els.forEach(async el=>{
		let input = el.querySelector("input, select")
		let value = input.value
		if (input.type == "number"){
			value = input.valueAsNumber
		}
		await eel.update_setting(input.name, value)
	})
	let mods = document.querySelectorAll("#mods .card")
	mods.forEach(async mod=>{
		let mod_id = mod.getAttribute("id")
		let enable = mod.querySelector("input[name=enable]").checked
		let settings = {}
		mod.querySelectorAll(".settings .input-group").forEach(seti=>{
			let input = seti.querySelector("input, select")
			let value = input.value
			if (input.type == "number"){
				value = input.valueAsNumber
			}
			settings[input.name] = value
		})
		await eel.update_mod_setting(mod_id, enable, settings)()
	})
	await eel.save_settings()
	await eel.save_mods_settings()
	await eel.refresh()
}


async function buildSettings(){
	let settings = await eel.get_settings()();
	let parent = document.querySelector("#main")
	settings.forEach(s=>{
		let el = Setting(s)
		parent.appendChild(el)
	})
}

async function buildMods(){
	let mods = await eel.get_mods()();
	let parent = document.querySelector("#mods")
	mods.forEach(s=>{
		let el = Mod(s)
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

	let input = input_area.querySelector("input, select")
	input.name = data.name
	if (data.default){
		input.placeholder = data.default
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

function Mod(data){
	let div = document.createElement("div")
	div.className = "card"
	div.setAttribute("id", data.id)
	div.innerHTML = `
		<div class="row g-0">
			<div class="col-md-3 center">
				<img src="${data.icon}" class="img-fluid rounded">
			</div>
			<div class="col-md-7 center">
				<div class="card-body">
					<h5 class="card-title${data.description || data.author ? ' mb-2':''}">${data.name}</h5>
					${data.description ? `<div class="card-text">${data.description}</div>`:''}
					${data.author ? `<small class="text-body-secondary">${data.author}</small>`:''}
				</div>
			</div>
			<div class="col-md-2 gap-2 center" style="justify-content: flex-end;">
				${data.settings.length > 0 ? `
					<button type="button" class="btn btn-outline-secondary settings_button">
						<i class="bi bi-gear-fill"></i>
					</button>
				` : ""}
				<div class="form-switch">
					<input class="form-check-input" type="checkbox" name="enable" role="switch"${data.enable?' checked':''}>
				</div>
			</div>
		</div>

		<div class="accordion-collapse collapse">
			<div class="accordion-body settings"></div>
		</div>
	`
	if (data.settings.length > 0){
		let settings = div.querySelector(".settings")
		data.settings.forEach(s=>{
			let el = Setting(s)
			settings.appendChild(el)
		})
		let colapse = new bootstrap.Collapse(div.querySelector(".accordion-collapse"), {toggle: false})
		div.querySelector(".settings_button").onclick = _=>{colapse.toggle()}
	}
	return div
}

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
	parent.innerHTML = ""
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
	data.enable ? div.style.order = "-1" : null
	div.innerHTML = `
		<div class="row g-0 px-3 py-2">
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
				<button class="btn btn-outline-secondary settings_button">
					<i class="bi bi-gear-fill"></i>
				</button>
				<div class="form-switch">
					<input class="form-check-input" type="checkbox" name="enable" role="switch"${data.enable?' checked':''}>
				</div>
			</div>
		</div>
		<div class="accordion-collapse collapse">
			<div class="accordion-body settings d-flex flex-column gap-2 p-3"></div>
		</div>
	`
	let settings = div.querySelector(".settings")
	data.settings.forEach(s=>{
		let el = Setting(s)
		el.querySelector(".col-form-label").classList.replace("col-sm-4", "col-sm-3")
		settings.appendChild(el)
	})

	let delete_area = document.createElement("div")
	delete_area.className = "row"
	delete_area.innerHTML = `
		<label class="col-sm-3"></label>
		<div class="col">
			<button class="btn btn-danger w-75${data.settings.length > 0 ? " mt-2":""}">Delete</button>
		</div>
	`
	let del_but = delete_area.querySelector("button")
	del_but.onclick = async _=>{
		del_but.disabled = true
		del_but.innerHTML = `
			<span class="spinner-border spinner-border-sm"></span>
		`
		let success = await eel.remove_mod(data.id)()
		setTimeout(async _=>{
			del_but.disabled = false
			if (success){
				await eel.refresh()
				div.remove()
			} else {
				del_but.innerHTML = "Delete"
				alert("Error")
			}
		}, 250)
	}
	settings.appendChild(delete_area)

	let colapse = new bootstrap.Collapse(div.querySelector(".accordion-collapse"), {toggle: false})
	div.querySelector(".settings_button").onclick = _=>{colapse.toggle()}
	return div
}

async function closeModsStore(){
	document.querySelector("#mods_store").classList.remove("show")
	document.body.style.overflow = '';
	await eel.refresh()
	buildMods()
}
async function openModsStore(){
	document.querySelector("#mods_store").classList.add("show")
	document.body.style.overflow = 'hidden';
	let parent = document.querySelector("#mods_store .content")
	parent.innerHTML = ""
	let data = await eel.mods_store()()
	let installed = await eel.get_mods()();
	data.forEach(mod=>{
		let div = document.createElement("div")
		div.className = "card"
		installed.some(obj => obj.id == mod.id) ? null : div.style.order = "-1"
		div.innerHTML = `
			<div class="row g-0 py-2">
				<div class="col-md-3 center">
					<img src="${mod.icon}" class="img-fluid rounded">
				</div>
				<div class="col-md-6 center">
					<div class="card-body">
						<h5 class="card-title${mod.description || mod.author ? ' mb-2':''}">${mod.name}</h5>
						${mod.description ? `<div class="card-text">${mod.description}</div>`:''}
						${mod.author ? `<small class="text-body-secondary">${mod.author}</small>`:''}
					</div>
				</div>
				<div class="col-md-3 center">
					${installed.some(obj => obj.id == mod.id) ? `
						<button class="btn btn-danger action">Remove</button>
					` : `
						<button class="btn btn-primary action">Install</button>
					`
					}
				</div>
			</div>
		`
		let action = div.querySelector(".action")
		async function install_mod(){
			action.className = "btn btn-primary"
			action.disabled = true
			action.innerHTML = `
				<span class="spinner-border spinner-border-sm"></span>
			`
			let success = await eel.install_mod(mod.id)()
			action.disabled = false
			if (success){
				action.className = "btn btn-danger"
				action.innerHTML = "Remove"
				action.onclick = remove_mod
			} else {
				action.className = "btn btn-primary"
				action.innerHTML = "Install"
				alert("Error")
			}
		}
		async function remove_mod(){
			action.disabled = true
			action.innerHTML = `
				<span class="spinner-border spinner-border-sm"></span>
			`
			let success = await eel.remove_mod(mod.id)()
			setTimeout(_=>{
				action.disabled = false
				if (success){
					action.className = "btn btn-primary"
					action.innerHTML = "Install"
					action.onclick = install_mod
				} else {
					action.innerHTML = "Remove"
					alert("Error")
				}
			}, 250)
		}
		
		if (installed.some(obj => obj.id == mod.id)){
			action.onclick = remove_mod
		} else {
			action.onclick = install_mod
		}
		parent.appendChild(div)
	})
}

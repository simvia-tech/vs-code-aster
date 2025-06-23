let vscode;
let nameText;
let createButton;
let cancelButton;
let timeLimit, memoryLimit, ncpus, mpiNbcpu, mpiNbnoeud;
const formData = {
  name: '',
  parameters: {
    time_limit: '',
    memory_limit: '',
    ncpus: '',
    mpi_nbcpu: '',
    mpi_nbnoeud: ''
  },
  inputFiles: [],
  outputFiles: []
};


window.addEventListener('load', () => {
	// https://code.visualstudio.com/api/extension-guides/webview#scripts-and-message-passing
	try {
		vscode = acquireVsCodeApi();
	} catch (e) {
		// Not running as a VS Code webview - maybe testing in external browser.
		console.error(e.message);
	}
	//On mets les lignes pas directement dans le html mais ici (+ simple pour récupérer les 
	//données)
	modifyFileRows(true, true);
	modifyFileRows(true, true);
	modifyFileRows(true, false);

	nameText = document.getElementById('envName');
	createButton = document.getElementById('boutonCreation');
	cancelButton = document.getElementById('boutonAnnulation');
	addOutputFileButton = document.getElementById('addOutputFile');
	addInputFileButton = document.getElementById('addInputFile');
	removeOutputFileButton = document.getElementById('removeOutputFile');
	removeInputFileButton = document.getElementById('removeInputFile');
	timeLimit = document.getElementById('time_limit');
	memoryLimit = document.getElementById('memory_limit');
	ncpus = document.getElementById('ncpus');
	mpiNbcpu = document.getElementById('mpi_nbcpu');
	mpiNbnoeud = document.getElementById('mpi_nbnoeud');


	nameText.addEventListener('keyup', validate);
	nameText.addEventListener('change', validate);
	createButton.addEventListener('click', submitCreate);
	cancelButton.addEventListener('click', submitCancel);
	addOutputFileButton.addEventListener('click', () => modifyFileRows(true, false));
	addInputFileButton.addEventListener('click', () =>  modifyFileRows(true, true));
	removeOutputFileButton.addEventListener('click', () => modifyFileRows(false, false));
	removeInputFileButton.addEventListener('click', () => modifyFileRows(false, true));
	timeLimit.addEventListener('input', () => { formData.parameters.time_limit = timeLimit.value.trim(); });
	memoryLimit.addEventListener('input', () => { formData.parameters.memory_limit = memoryLimit.value.trim(); });
	ncpus.addEventListener('input', () => { formData.parameters.ncpus = ncpus.value.trim(); });
	mpiNbcpu.addEventListener('input', () => { formData.parameters.mpi_nbcpu = mpiNbcpu.value.trim(); });
	mpiNbnoeud.addEventListener('input', () => { formData.parameters.mpi_nbnoeud = mpiNbnoeud.value.trim(); });
	nameText.addEventListener('input', () => { formData.name = nameText.value.trim(); });
});

// function submitCreate() {
// 	// TODO: Fill in other result properties.
// 	//A FAIRE : ici récupérer la data et créer le fichier ?

// 	const result = {
// 		name: nameText.value
// 	};
// 	vscode.postMessage({ command: 'result', value: "result" });
	
// }

function modifyFileRows(add, input) {
  const container = document.getElementById(input ? 'inputFilesContainer' : 'outputFilesContainer');
  const targetArray = input ? formData.inputFiles : formData.outputFiles;

  if (add) {
    addFileRow(container, targetArray);
  } else {
    removeFileRow(container, targetArray);
  }
}


function addFileRow(container, targetArray) {
  const div = document.createElement('div');
  div.className = 'field';

  const select = document.createElement('select');
  select.innerHTML = `
    <option value="nom">nom</option>
    <option value="comm">comm</option>
    <option value="mmed">mmed</option>
    <option value="rmed">rmed</option>
  `;
  div.appendChild(select);

  const inputName = document.createElement('input');
  inputName.type = 'text';
  inputName.placeholder = 'Nom Fichier';
  div.appendChild(inputName);

  const inputUnit = document.createElement('input');
  inputUnit.type = 'text';
  inputUnit.placeholder = 'Unit';
  div.appendChild(inputUnit);

  container.appendChild(div);

  const fileObj = { type: '', name: '', unit: '' };

  select.addEventListener('input', () => fileObj.type = select.value.trim());
  inputUnit.addEventListener('input', () => fileObj.unit = inputUnit.value.trim());

  if (targetArray === formData.inputFiles) {
	inputName.addEventListener('input', (event) => {
			fileObj.name = inputName.value.trim();
			handleFileNameInput(event.target);
		});
  } else {
	inputName.addEventListener('input', () => fileObj.name = inputName.value.trim());
  }

  targetArray.push(fileObj);

}

function removeFileRow(container, targetArray) {
  if (container.lastElementChild) {
    container.removeChild(container.lastElementChild);
	targetArray.pop();
  }
}

function handleFileNameInput(inputElement) {
	const partial = inputElement.value;
	lastActiveInput = inputElement;

	vscode.postMessage({
		command: 'autocomplete',
		value: partial
	});
}

window.addEventListener('message', event => {
	const message = event.data;
	if (message.command === 'autocompleteResult') {
		showSuggestions(message.suggestions, lastActiveInput);
	}
});

function showSuggestions(suggestions, input) {
	// Crée ou met à jour une dropdown sous l'input
	// (à toi de styler ça joliment en CSS)
}


function submitCreate() {
  const lines = [];

  // Nom (si nécessaire)
  if (formData.name) {
    lines.push(`P name ${formData.name}`);
  }

  // Paramètres
  for (const [key, val] of Object.entries(formData.parameters)) {
    if (val) lines.push(`P ${key} ${val}`);
  }

  // Fichiers d'entrée
  formData.inputFiles.forEach(f => {
    if (true) {
      lines.push(`F ${f.type} ${f.name} D ${f.unit}`);
    }
  });

  // Fichiers de sortie
  formData.outputFiles.forEach(f => {
    if (true) {
      lines.push(`F ${f.type} ${f.name} R ${f.unit}`);
    }
  });

  vscode.postMessage({ command: 'result', value: lines.join('\n') });
}


function submitCancel() {
	vscode.postMessage({ command: 'cancel' });
}

function validate() {
	const isValid = !!nameText.value;
	createButton.disabled = !isValid;
}

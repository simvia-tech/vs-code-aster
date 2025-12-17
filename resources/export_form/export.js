let vscode;
let nameText, createButton, cancelButton;
let timeLimit, memoryLimit, ncpus, mpiNbcpu, mpiNbnoeud;
let lastActiveInput = null;

const allowedTypes = ['nom', 'comm', 'med', 'msh', 'datg', 'dat', 'rmed', 'mmed', 'base','mess', 'libr'];
const defaultUnits = {
    nom: '0', comm: '1', med: '20', msh: '19', datg: '16', dat: '29',
    rmed: '80', base: '0', mess: '6', mmed: '20', libr : '16'
};

const formData = {
    name: '',
    parameters: { time_limit: '300', memory_limit: '1024', ncpus: '1', mpi_nbcpu: '4', mpi_nbnoeud: '1' },
    inputFiles: [],
    outputFiles: []
};

let existingFiles = [];


// Initialize form and attach event listeners
window.addEventListener('load', () => {
	try {
		vscode = acquireVsCodeApi();
	} catch (e) {
		console.error(e.message);
	}

    // Create initial input/output file rows
	modifyFileRows(true, true);
	modifyFileRows(true, true);
	modifyFileRows(true, false);
    formData.name = "simvia.export";

    // DOM elements
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
    validate();

	createButton.addEventListener('click', submitCreate);
	cancelButton.addEventListener('click', submitCancel);

	addOutputFileButton.addEventListener('click', () => modifyFileRows(true, false));
	addInputFileButton.addEventListener('click', () =>  modifyFileRows(true, true));
	removeOutputFileButton.addEventListener('click', () => modifyFileRows(false, false));
	removeInputFileButton.addEventListener('click', () => modifyFileRows(false, true));

    // Update form data on input changes
    nameText.addEventListener('input', () => { formData.name = nameText.value.trim(); });
    timeLimit.addEventListener('input', () => { formData.parameters.time_limit = timeLimit.value.trim(); verifyValueInput(timeLimit, formData.parameters.time_limit); });
    memoryLimit.addEventListener('input', () => { formData.parameters.memory_limit = memoryLimit.value.trim(); verifyValueInput(memoryLimit, formData.parameters.memory_limit); });
    ncpus.addEventListener('input', () => { formData.parameters.ncpus = ncpus.value.trim(); verifyValueInput(ncpus, formData.parameters.ncpus); });
    mpiNbcpu.addEventListener('input', () => { formData.parameters.mpi_nbcpu = mpiNbcpu.value.trim(); verifyValueInput(mpiNbcpu, formData.parameters.mpi_nbcpu); });
    mpiNbnoeud.addEventListener('input', () => { formData.parameters.mpi_nbnoeud = mpiNbnoeud.value.trim(); verifyValueInput(mpiNbnoeud, formData.parameters.mpi_nbnoeud); });
  });

function verifyValueInput(inputItem, value) {
  const intVal = Number(value);
  if (Number.isInteger(intVal)) {
    inputItem.classList.remove('input-warning');
	}
  else {
    inputItem.classList.add('input-warning');
	}
}

// Add or remove file rows dynamically
function modifyFileRows(add, input, fileObj) {
  const container = document.getElementById(input ? 'inputFilesContainer' : 'outputFilesContainer');
  const targetArray = input ? formData.inputFiles : formData.outputFiles;

  if (add) {
    addFileRow(container, targetArray, fileObj);
  } else {
    removeFileRow(container, targetArray);
  }
}

// Dynamic creation of file input row with type/unit handling
function addFileRow(container, targetArray, fileObj) {

  const copy = fileObj ? true : false;
  const wrapper = document.createElement('div');
  wrapper.className = 'field';
  wrapper.style.display = 'flex';
  wrapper.style.flexDirection = 'column';
  wrapper.style.gap = '4px';

  const row = document.createElement('div');
  row.className = 'file-row';
  row.style.display = 'flex';
  row.style.flexDirection = 'row';
  row.style.gap = '14px';
  row.style.alignItems = 'center';

  const select = document.createElement('select');

  select.innerHTML = allowedTypes.map(type => `<option value="${type}">${type}</option>`).join('');
  
  row.appendChild(select);

  const nameWrapper = document.createElement('div');
  nameWrapper.style.display = 'flex';
  nameWrapper.style.flexDirection = 'column';
  nameWrapper.style.position = 'relative';

  const inputName = document.createElement('input');
  inputName.type = 'text';
  nameWrapper.appendChild(inputName);
  row.appendChild(nameWrapper);

  const inputUnit = document.createElement('input');
  inputUnit.type = 'text';
  row.appendChild(inputUnit);

  wrapper.appendChild(row);
  container.appendChild(wrapper);

  if (copy) {
    const type = allowedTypes.includes(fileObj.type) ? fileObj.type : 'nom';
    select.value = type;
    inputName.value = fileObj.name;
    inputUnit.value = fileObj.unit;
  }

  else {
    fileObj = { type: 'nom', name: '', unit: '0' };
    inputName.placeholder = 'File Name : ';
    inputUnit.value = '0';
  }

  select.addEventListener('input', () => {fileObj.type = select.value.trim();
    const unit = defaultUnits[fileObj.type];
    inputUnit.value = unit;
    fileObj.unit = unit;
  });
  inputUnit.addEventListener('input', () => {const value = inputUnit.value.trim();
    verifyValueInput(inputUnit, inputUnit.value.trim());
    fileObj.unit = value;
  });

  inputName.fileObj = fileObj;

  if (targetArray === formData.inputFiles) {

    const triggerHandle = () => {
      fileObj.name = inputName.value.trim();
      handleFileNameInput(inputName);
    };

    inputName.addEventListener('input', triggerHandle);
    inputName.addEventListener('focus', triggerHandle);

    inputName.addEventListener('blur', () => {
      // 100 ms delay to allow clicking on a suggestion
      // without this, the suggestions would disappear before the click registers
      setTimeout(() => removeSuggestions(), 100); 
    });

  } else {
    inputName.addEventListener('input', () => fileObj.name = inputName.value.trim());
  }
  if (!copy) {
    targetArray.push(fileObj);
  }
}


function removeFileRow(container, targetArray) {
  if (container.lastElementChild) {
    container.removeChild(container.lastElementChild);
	  targetArray.pop();
  }
}

function handleFileNameInput(inputElement) {
	lastActiveInput = inputElement;
  const row  = inputElement.parentElement?.parentElement;
  const select = row?.querySelector('select');
  const selectedType = select ? select.value.trim() : '';

	vscode.postMessage({
		command: 'autocomplete',
		value: inputElement.value,
    type: selectedType
	});
}

function removeSuggestions() {
    const existing = lastActiveInput.parentElement.querySelector('.suggestion-box');
    if (existing) {
      existing.remove();
    }
}

window.addEventListener('message', event => {
	const message = event.data;

	if (message.command === 'autocompleteResult') {
    lastActiveInput.classList.remove('input-warning');
		showSuggestions(message.suggestions, lastActiveInput);
	}

  if (message.command === 'autocompleteFailed') {
    lastActiveInput.classList.add('input-warning');
    const existing = lastActiveInput.parentElement.querySelector('.suggestion-box');
    if (existing) {
      existing.remove();
    }
	}

  if (message.command === 'verifyFileNames') {
    existingFiles = message.files;
	}
  
  if (message.command === 'exportFileAlreadyDefined') {
    copyExportFile(message.formData);
  }
});

function copyExportFile(exportData) {
  formData.name = exportData.name;
  formData.parameters = { ...exportData.parameters };

  const nameText = document.getElementById('envName');
  const timeLimit = document.getElementById('time_limit');
  const memoryLimit = document.getElementById('memory_limit');
  const ncpus = document.getElementById('ncpus');
  const mpiNbcpu = document.getElementById('mpi_nbcpu');
  const mpiNbnoeud = document.getElementById('mpi_nbnoeud');

  if (nameText && formData.name) {
    nameText.value = formData.name;
  }
  if (timeLimit && formData.parameters.time_limit) {
    timeLimit.value = formData.parameters.time_limit;
  }
  if (memoryLimit && formData.parameters.memory_limit) {
    memoryLimit.value = formData.parameters.memory_limit;
  }
  if (ncpus && formData.parameters.ncpus) {
    ncpus.value = formData.parameters.ncpus;
  }
  if (mpiNbcpu && formData.parameters.mpi_nbcpu) {
    mpiNbcpu.value = formData.parameters.mpi_nbcpu;
  }
  if (mpiNbnoeud && formData.parameters.mpi_nbnoeud) {
    mpiNbnoeud.value = formData.parameters.mpi_nbnoeud;
  }

  if (exportData.inputFiles.length > 0 || exportData.outputFiles.length > 0) {
    modifyFileRows(false, true);
    modifyFileRows(false, true);
    modifyFileRows(false, false);
  }

  for (const file of exportData.inputFiles) {
    const fileObj = {type: file.type, name: file.name, unit: file.unit};
    formData.inputFiles.unshift(fileObj);
    modifyFileRows(true, true, fileObj);
  }
  
  for (const file of exportData.outputFiles) {
    const fileObj = {type: file.type, name: file.name, unit: file.unit};
    formData.outputFiles.unshift(fileObj);
    modifyFileRows(true, false, fileObj);
  }

}


function showSuggestions(suggestions, inputElement) {
  const existing = inputElement.parentElement.querySelector('.suggestion-box');
  if (existing) {
    existing.remove();
  }

  const box = document.createElement('div');
  box.className = 'suggestion-box';

  Object.assign(box.style, {
    position: 'absolute',
    top: '100%',
    left: '0',
    zIndex: '10',
    border: '1px solid #ccc',
    padding: '4px',
    backgroundColor: '#fff',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    minWidth: `${inputElement.offsetWidth}px`,
  });

  const items = suggestions.map((s, index) => {
    const item = document.createElement('div');
    item.textContent = s;
    item.style.padding = '2px 4px';
    item.style.cursor = 'pointer';
    if (index === 0) {
      item.classList.add('highlighted-suggestion');
    }
    box.appendChild(item);
    return item;
  });

  let selectedIndex = 0;

  const updateHighlight = () => {
    items.forEach((el, i) =>
      el.classList.toggle('highlighted-suggestion', i === selectedIndex)
    );
  };

  inputElement.addEventListener('keydown', function handleKeyDown(event) {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      selectedIndex = (selectedIndex + 1) % items.length;
      updateHighlight();
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      selectedIndex = (selectedIndex - 1 + items.length) % items.length;
      updateHighlight();
    } else if (event.key === 'Enter' || event.key === 'ArrowRight'
      ||event.key === 'Tab') {
      event.preventDefault();
      inputElement.value = suggestions[selectedIndex];
      inputElement.removeEventListener('keydown', handleKeyDown);
      inputElement.fileObj.name = inputElement.value;
      box.remove();
    }
  });

  items.forEach((item, index) => {
    item.addEventListener('click', () => {
      inputElement.value = suggestions[index];
      inputElement.fileObj.name = inputElement.value;
      box.remove();
    });
  });

  inputElement.parentElement.appendChild(box);
}




function submitCreate() {
  const errorMsg = checkFields();

  if (errorMsg) {
    vscode.postMessage({ command: 'wrongCreation', value: errorMsg });
  }
  else {
    const lines = [];
    const filename = formData.name;
    lines.push(filename);

    for (const [key, value] of Object.entries(formData.parameters)) {
      lines.push(`P ${key} ${value}`);
    }

    for (const file of formData.inputFiles) {
      lines.push(`F ${file.type} ${file.name} D ${file.unit}`);
    }

    for (const file of formData.outputFiles) {
      lines.push(`F ${file.type} ${file.name} R ${file.unit}`);
    } 

    const content = lines.join('\n');
    vscode.postMessage({ command: 'result', value: content});
  }
}

function checkFields() {

  for (const [key, value] of Object.entries(formData.parameters)) {
    const intVal = Number(value.trim());
    if (!value || !Number.isInteger(intVal)) {
      return `The parameter "${key}" must be an integer.`;
    }
  }

  for (let i = 0; i < formData.inputFiles.length; i++) {
    const file = formData.inputFiles[i];
    if (!file.name) {
      return `Input file #${i + 1} is invalid: missing file name.`;
    }
    const intVal = Number(file.unit.trim());
    if (!Number.isInteger(intVal)) {
      return `Input file #${i + 1} is invalid: unit must be an integer.`;
    }
    let alreadyUsed = formData.outputFiles.some(test => Number(file.unit) !== 0 && test.unit === file.unit);
    for (let j = 0; j < formData.inputFiles.length; j++) {
      if (intVal && i !== j && formData.inputFiles[j].unit === file.unit) {
        alreadyUsed = true;
        break;
      }
    }
    if (alreadyUsed) {
      return `Input file #${i + 1} is invalid: ${intVal} is already used as a unit value.`;
    }
  }

  for (let i = 0; i < formData.outputFiles.length; i++) {
    const file = formData.outputFiles[i];
    if (!file.name) {
      return `Output file #${i + 1} is invalid: missing file name.`;
    }
    const intVal = Number(file.unit.trim());
    if (!Number.isInteger(intVal)) {
      return `Output file #${i + 1} is invalid: unit must be an integer.`;
    }
    let alreadyUsed = formData.inputFiles.some(test => Number(file.unit) !== 0 && test.unit === file.unit);
    for (let j = 0; j < formData.outputFiles.length; j++) {
      if (intVal && i !== j && formData.outputFiles[j].unit === file.unit) {
        alreadyUsed = true;
        break;
      }
    }
    if (alreadyUsed) {
      return `Output file #${i + 1} is invalid: ${intVal} is already used as a unit value.`;
    }

  }

  return '';
}


function submitCancel() {
	vscode.postMessage({ command: 'cancel' });
}

function validate() {
	const isValid = !!nameText.value;
	createButton.disabled = !isValid;
}

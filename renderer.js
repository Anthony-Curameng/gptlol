const state = {
  document: {
    title: '',
    columns: [],
    rows: []
  },
  currentPath: ''
};

const boardTitleInput = document.querySelector('#board-title');
const fileStatus = document.querySelector('#file-status');
const columnRow = document.querySelector('#column-row');
const boardBody = document.querySelector('#board-body');
const addColumnButton = document.querySelector('#add-column');
const addRowButton = document.querySelector('#add-row');
const newDocumentButton = document.querySelector('#new-document');
const openDocumentButton = document.querySelector('#open-document');
const saveDocumentButton = document.querySelector('#save-document');
const pinWindowToggle = document.querySelector('#pin-window');

const columnHeaderTemplate = document.querySelector('#column-header-template');
const cellTemplate = document.querySelector('#cell-template');
const rowActionTemplate = document.querySelector('#row-action-template');

function createRow(columns) {
  const values = {};
  columns.forEach((column) => {
    values[column] = '';
  });

  return {
    id: `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
    values
  };
}

function normalizeDocument(doc) {
  const columns = Array.isArray(doc?.columns) && doc.columns.length > 0
    ? doc.columns.map((column, index) => String(column || `Column ${index + 1}`))
    : ['Road Name', 'Category', 'Arrangement', 'Spacing'];

  const rows = Array.isArray(doc?.rows)
    ? doc.rows.map((row, rowIndex) => {
        const values = {};
        columns.forEach((column) => {
          values[column] = String(row?.values?.[column] ?? '');
        });

        return {
          id: String(row?.id ?? `${Date.now()}-${rowIndex}`),
          values
        };
      })
    : [createRow(columns)];

  return {
    title: String(doc?.title || 'Project Spacing Board'),
    columns,
    rows: rows.length > 0 ? rows : [createRow(columns)]
  };
}

function updateFileStatus() {
  fileStatus.textContent = state.currentPath
    ? `Editing ${state.currentPath}`
    : 'Using an unsaved board.';
}

function getDocumentPayload() {
  return {
    title: state.document.title,
    columns: [...state.document.columns],
    rows: state.document.rows.map((row) => ({
      id: row.id,
      values: { ...row.values }
    }))
  };
}

function renameColumn(previousName, nextName) {
  if (!nextName || previousName === nextName) {
    return;
  }

  if (state.document.columns.includes(nextName)) {
    render();
    return;
  }

  state.document.columns = state.document.columns.map((column) => (
    column === previousName ? nextName : column
  ));

  state.document.rows.forEach((row) => {
    row.values[nextName] = row.values[previousName] ?? '';
    delete row.values[previousName];
  });
}

function removeColumn(columnName) {
  if (state.document.columns.length === 1) {
    return;
  }

  state.document.columns = state.document.columns.filter((column) => column !== columnName);
  state.document.rows.forEach((row) => {
    delete row.values[columnName];
  });
  render();
}

function addColumn() {
  const baseName = 'New Column';
  let name = baseName;
  let index = 1;

  while (state.document.columns.includes(name)) {
    index += 1;
    name = `${baseName} ${index}`;
  }

  state.document.columns.push(name);
  state.document.rows.forEach((row) => {
    row.values[name] = '';
  });
  render();
}

function removeRow(rowId) {
  state.document.rows = state.document.rows.filter((row) => row.id !== rowId);
  if (state.document.rows.length === 0) {
    state.document.rows.push(createRow(state.document.columns));
  }
  render();
}

function addRow() {
  state.document.rows.push(createRow(state.document.columns));
  render();
}

function render() {
  boardTitleInput.value = state.document.title;
  updateFileStatus();
  columnRow.innerHTML = '';
  boardBody.innerHTML = '';

  state.document.columns.forEach((columnName) => {
    const headerFragment = columnHeaderTemplate.content.cloneNode(true);
    const titleInput = headerFragment.querySelector('.column-title');
    const removeButton = headerFragment.querySelector('.remove-column');

    titleInput.value = columnName;
    titleInput.addEventListener('change', (event) => {
      const nextName = event.target.value.trim() || columnName;
      renameColumn(columnName, nextName);
      render();
    });

    removeButton.addEventListener('click', () => {
      removeColumn(columnName);
    });

    columnRow.appendChild(headerFragment);
  });

  const actionsHeader = document.createElement('th');
  actionsHeader.textContent = '';
  columnRow.appendChild(actionsHeader);

  state.document.rows.forEach((row) => {
    const tr = document.createElement('tr');

    state.document.columns.forEach((columnName) => {
      const cellFragment = cellTemplate.content.cloneNode(true);
      const textarea = cellFragment.querySelector('.cell-input');

      textarea.value = row.values[columnName] ?? '';
      textarea.placeholder = `${columnName} notes...`;
      textarea.addEventListener('input', (event) => {
        row.values[columnName] = event.target.value;
      });

      tr.appendChild(cellFragment);
    });

    const rowActionFragment = rowActionTemplate.content.cloneNode(true);
    rowActionFragment.querySelector('.remove-row').addEventListener('click', () => {
      removeRow(row.id);
    });

    tr.appendChild(rowActionFragment);
    boardBody.appendChild(tr);
  });
}

boardTitleInput.addEventListener('input', (event) => {
  state.document.title = event.target.value;
});

addColumnButton.addEventListener('click', addColumn);
addRowButton.addEventListener('click', addRow);
newDocumentButton.addEventListener('click', async () => {
  const defaultDocument = await window.projectBoardApi.getDefaultDocument();
  state.document = normalizeDocument(defaultDocument);
  state.currentPath = '';
  render();
});

openDocumentButton.addEventListener('click', async () => {
  try {
    const result = await window.projectBoardApi.openJson();
    if (result.canceled) {
      return;
    }

    state.document = normalizeDocument(result.data);
    state.currentPath = result.filePath;
    render();
  } catch (error) {
    fileStatus.textContent = `Could not open JSON: ${error.message}`;
  }
});

saveDocumentButton.addEventListener('click', async () => {
  try {
    const suggestedPath = state.currentPath || `${state.document.title || 'project-spacing-board'}.json`;
    const result = await window.projectBoardApi.saveJson({
      suggestedPath,
      data: getDocumentPayload()
    });

    if (!result.canceled) {
      state.currentPath = result.filePath;
      updateFileStatus();
    }
  } catch (error) {
    fileStatus.textContent = `Could not save JSON: ${error.message}`;
  }
});

pinWindowToggle.addEventListener('change', async (event) => {
  const isPinned = await window.projectBoardApi.setAlwaysOnTop(event.target.checked);
  pinWindowToggle.checked = isPinned;
});

async function initialize() {
  const [defaultDocument, isPinned] = await Promise.all([
    window.projectBoardApi.getDefaultDocument(),
    window.projectBoardApi.getAlwaysOnTop()
  ]);

  state.document = normalizeDocument(defaultDocument);
  pinWindowToggle.checked = isPinned;
  render();
}

initialize();

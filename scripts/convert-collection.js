const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

const COLLECTION_DIR = path.join(__dirname, '../postman/collections/Django Form Creator API');
const OUTPUT_FILE = path.join(__dirname, '../postman/django-form-creator.collection.json');

function readYamlRequests(folder) {
  const folderPath = path.join(COLLECTION_DIR, folder);
  const files = fs.readdirSync(folderPath).filter(f => f.endsWith('.request.yaml'));
  return files
    .map(f => {
      const raw = yaml.load(fs.readFileSync(path.join(folderPath, f), 'utf8'));
      return raw;
    })
    .sort((a, b) => (a.order || 0) - (b.order || 0));
}

function buildItem(req) {
  const item = {
    name: req.name,
    request: {
      method: req.method,
      header: (req.headers || []).map(h => ({ key: h.key, value: h.value })),
      url: { raw: req.url, host: [req.url] },
    },
  };

  if (req.body && req.body.type === 'json') {
    item.request.body = {
      mode: 'raw',
      raw: req.body.content,
      options: { raw: { language: 'json' } },
    };
  }

  const testScript = (req.scripts || []).find(s => s.type === 'afterResponse');
  if (testScript) {
    item.event = [
      {
        listen: 'test',
        script: { type: 'text/javascript', exec: testScript.code.split('\n') },
      },
    ];
  }

  return item;
}

const folders = fs.readdirSync(COLLECTION_DIR).filter(f =>
  fs.statSync(path.join(COLLECTION_DIR, f)).isDirectory()
);

const collection = {
  info: {
    name: 'Django Form Creator API',
    schema: 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json',
  },
  item: folders.map(folder => ({
    name: folder,
    item: readYamlRequests(folder).map(buildItem),
  })),
};

fs.writeFileSync(OUTPUT_FILE, JSON.stringify(collection, null, 2));
console.log(`Collection written to: ${OUTPUT_FILE}`);
console.log(`Folders: ${folders.join(', ')}`);
const totalRequests = folders.reduce((sum, f) => sum + readYamlRequests(f).length, 0);
console.log(`Total requests: ${totalRequests}`);

/***
 *  OC Single Variant Input Widget
 *  This code will initialize the OC single variant input widget on a page that contains a valid container.
 *
 *  To use:
 *    1. add empty container to html file -
 *    <div id='oc-svi'></div>
 *    2. include this file as a script
 *    <script src="oc-svi.js" type="application/javascript" defer></script>
 *    3. include the stylesheet
 *    <link rel="stylesheet" type="text/css" href="oc-svi.css" />
 **/

// Base URL for the single variant page
const API_URL = 'https://run.opencravat.org/webapps/variantreport/index.html';
// types of input allowed
class TYPES {
    static DBSNP = 'dbsnp';
    static CLINGEN = 'clingen';
    static HGVS = 'hgvs';
    static COORDS = 'coords';
    static ERROR = 'error';
}

// validate rsid input
function isDbSnp(input) {
    return input.substring(0, 2) === 'rs';
}

// validate clingen allele registry input
function isClingenAlleleRegistry(input) {
    return input.substring(0, 2) === 'ca';
}

// validate hgvs input, want something of the form: AAAA:c.2134a>c
function isHGVS(input) {
    const validSequenceTypes = ['c', 'g', 'm', 'n', 'o', 'p', 'r'];
    // check that the first token is something like aaaa:X.bbb where X is a valid reference sequence type
    let parts = input.split(':');
    if (parts.length !== 2) {
        return false;
    }
    let descriptionParts = parts[1].split('.');
    if (descriptionParts.length !== 2) {
        return false;
    }
    if (!validSequenceTypes.includes(descriptionParts[0])) {
        return false;
    }
    return true;
}

// parse a chromosome for coordinate input, anything from 1-22, x, y, m, mt
// 'chr' prefix optional
function findChromosome(id) {
    const validChroms = [
        '1', '2', '3', '4', '5', '6', '7', '8', '9',
        '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
        '20', '21', '22', 'x', 'y', 'm'
    ];
    let idOnly = id.startsWith('chr') ? id.substring(3) : id;
    if (idOnly === 'mt') { idOnly = 'm'; }
    if (!validChroms.includes(idOnly)) {
        return false;
    }
    return `chr${idOnly}`;
}

// parse coordinates input
// Expect four tokens corresponding to: 1. chromosome, 2. position, 3. reference base, 4. alternate base
// 1. Chromosome should be a valid chromosome (from findChromosome)
// 2. Position must be an integer
// 3. / 4. Reference and alternate bases should be in (a, c, g, t)
// Valid separators of the tokens are (' ', '\t', ':', '.', ';')
// Deletions should be written with correct reference base and '-' as alternate base
// Insertions should be written with '-' as reference base
// Duplications should be written as insertions
function parseCoordinates(input) {
    // split by multiple separator characters
    const parts = input.split(':').join(';')
        .split('.').join(';')
        .split(' ').join(';')
        .split('\t').join(';')
        .split(';');
    if (parts.length !== 4) {
        return false;
    }
    let chromosome = findChromosome(parts[0]);
    if (chromosome === false) { return false; }
    if (Number.isNaN(Number.parseInt(parts[1]))) { return false; }
    const validBasesRegex = /^[acgt-]+$/;
    if (!validBasesRegex.test(parts[2])) { return false; }
    if (!validBasesRegex.test(parts[3])) { return false; }

    return parts;
}

function determineInputType(input) {
    if (isDbSnp(input)) {
        return TYPES.DBSNP;
    }
    if (isClingenAlleleRegistry(input)) {
        return TYPES.CLINGEN;
    }
    if (isHGVS(input)) {
        return TYPES.HGVS;
    }
    if (parseCoordinates(input)) {
        return TYPES.COORDS;
    }
    return TYPES.ERROR;
}

// format hgvs string for url
// Everything will be uppercase except for the c. prefix, then will be url encoded
function formatHgvs(hgvs) {
    const hgvsParts = hgvs.toUpperCase().split(':');
    const prefix = hgvsParts[1][0].toLowerCase();
    const end = hgvsParts[1].substring(1);
    const total = `${hgvsParts[0]}:${prefix}${end}`;
    return encodeURIComponent(total);
}

// build url based on the input type
function buildUrl(inputType, input) {
    if (inputType === TYPES.HGVS) {
        const encoded = formatHgvs(input);
        return `${API_URL}?hgvs=${encoded}`;
    }
    if (inputType === TYPES.CLINGEN) {
        return `${API_URL}?clingen=${input}`;
    }
    if (inputType === TYPES.DBSNP) {
        return `${API_URL}?dbsnp=${input}`;
    }
    if (inputType === TYPES.COORDS) {
        const parts = parseCoordinates(input);
        const assembly = document.getElementById('oc-svi-assembly').value;
        return `${API_URL}?assembly=${assembly}&chrom=${parts[0]}&pos=${parts[1]}&ref_base=${parts[2]}&alt_base=${parts[3]}`;
    }
}

// try to determine the input type and do some quick validation, then either show an error or
// open a link to the single variant page
function handleSubmit(event) {
    const originalInput = document.getElementById('oc-svi-input').value;
    const input = originalInput.trim().toLowerCase();
    const inputType = determineInputType(input);

    if (inputType === TYPES.ERROR) {
        let error = document.getElementById('oc-svi-error');
        error.style.display = '';
    } else {
        const url = buildUrl(inputType, input);
        let error = document.getElementById('oc-svi-error');
        error.textContent = `input: ${input}, type: ${inputType} url: ${url}`;
        error.style.display = '';
        window.open(url, '_blank');
    }
    event.preventDefault();
}

// entry point, on document.ready, find the oc-svi container and replace it's html content with our
// single input form and attach handlers to the newly created objects.
document.addEventListener('DOMContentLoaded', ()  => {
    let inputContainer = document.getElementById('oc-svi');
    if (!inputContainer) return;

    inputContainer.innerHTML = `
        <form id="oc-svi-form">
            <input id="oc-svi-input" type="text" placeholder="Enter a variant HGVS, rsID, Clingen Allele Registry ID, or genomic coordinates." />
            <select name="oc-svi-assembly" id="oc-svi-assembly">
                <option value="hg38">hg38</option>
                <option value="hg19">hg19</option>
            </select>
            <button id="oc-submit-button" type="submit">Submit</button>
        </form>
        <div id="oc-svi-error" style="display: none">
            Could not determine input type. Please see our <button id="oc-svi-error-examples-btn" type="button">examples</button> check your input.
        </div>
        `;
    document.getElementById('oc-svi-form').addEventListener('submit', handleSubmit);
    document.getElementById('oc-submit-button').addEventListener('click', handleSubmit);
});
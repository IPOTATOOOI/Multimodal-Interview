import JSZip from 'jszip'

const WORD_TEXT_PART_RE = /^word\/(?:document|header\d+|footer\d+|footnotes|endnotes)\.xml$/

const XML_MIME = 'application/xml'
const DOCX_MIME = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

export async function extractDocxTextNodes(file) {
  const zip = await JSZip.loadAsync(await file.arrayBuffer())
  const parts = getTextParts(zip)
  const nodes = []
  const parser = new DOMParser()

  for (const partName of parts) {
    const xml = await zip.file(partName).async('string')
    const doc = parser.parseFromString(xml, XML_MIME)
    const textNodes = Array.from(doc.getElementsByTagName('w:t'))

    textNodes.forEach((node, index) => {
      const text = node.textContent || ''
      const normalized = normalizeText(text)
      if (!normalized) return

      nodes.push({
        id: `${partName}#${index}`,
        part: partName,
        index,
        text,
        normalized,
        context: getParagraphText(node),
      })
    })
  }

  return nodes
}

export function buildPlainResumeText(nodes) {
  const seen = new Set()
  return nodes
    .map((node) => node.context || node.normalized)
    .filter((text) => {
      const normalized = normalizeText(text)
      if (!normalized || seen.has(normalized)) return false
      seen.add(normalized)
      return true
    })
    .join('\n')
}

export function buildAiCandidateNodes(nodes, maxNodes = 180) {
  return nodes
    .filter((node) => node.normalized.length >= 2)
    .slice(0, maxNodes)
    .map((node) => ({
      id: node.id,
      text: limitText(node.normalized, 260),
      context: limitText(normalizeText(node.context), 320),
    }))
}

export async function applyDocxTextPatches(file, patches) {
  const zip = await JSZip.loadAsync(await file.arrayBuffer())
  const parser = new DOMParser()
  const serializer = new XMLSerializer()
  const patchesByPart = groupAcceptedPatches(patches)

  for (const [partName, partPatches] of patchesByPart.entries()) {
    const part = zip.file(partName)
    if (!part) continue

    const xml = await part.async('string')
    const doc = parser.parseFromString(xml, XML_MIME)
    const textNodes = Array.from(doc.getElementsByTagName('w:t'))

    partPatches.forEach((patch) => {
      const node = textNodes[patch.index]
      if (!node) return
      const replacement = normalizeReplacement(patch.replacement)
      node.textContent = replacement
      if (/^\s|\s$/.test(replacement)) {
        node.setAttribute('xml:space', 'preserve')
      }
    })

    zip.file(partName, serializer.serializeToString(doc))
  }

  return zip.generateAsync({
    type: 'blob',
    mimeType: DOCX_MIME,
    compression: 'DEFLATE',
  })
}

export function downloadBlob(blob, fileName) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

function getTextParts(zip) {
  return Object.keys(zip.files)
    .filter((name) => WORD_TEXT_PART_RE.test(name) && !zip.files[name].dir)
    .sort((a, b) => {
      if (a === 'word/document.xml') return -1
      if (b === 'word/document.xml') return 1
      return a.localeCompare(b)
    })
}

function groupAcceptedPatches(patches) {
  const grouped = new Map()

  patches
    .filter((patch) => patch.accepted !== false && patch.nodeId && patch.replacement != null)
    .forEach((patch) => {
      const [partName, indexValue] = String(patch.nodeId).split('#')
      const index = Number(indexValue)
      if (!partName || Number.isNaN(index)) return
      if (!grouped.has(partName)) grouped.set(partName, [])
      grouped.get(partName).push({ ...patch, index })
    })

  return grouped
}

function getParagraphText(textNode) {
  let current = textNode.parentNode
  while (current && current.nodeName !== 'w:p') current = current.parentNode
  if (!current) return textNode.textContent || ''

  return Array.from(current.getElementsByTagName('w:t'))
    .map((node) => node.textContent || '')
    .join('')
}

function normalizeText(text) {
  return String(text || '')
    .replace(/\s+/g, ' ')
    .trim()
}

function normalizeReplacement(text) {
  return String(text || '').replace(/[\r\n\t]+/g, ' ')
}

function limitText(text, maxLength) {
  if (!text || text.length <= maxLength) return text
  return `${text.slice(0, maxLength)}...`
}

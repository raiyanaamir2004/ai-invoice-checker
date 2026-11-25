// Turns the AI's text answer into clean fields we can work with.
return $input.all().map(item => {
  let content = item.json.choices?.[0]?.message?.content ?? '';
  // Some models wrap JSON in ```json ... ``` – remove that if present
  content = content.replace(/^\s*```(?:json)?\s*/i, '').replace(/\s*```\s*$/, '');
  try {
    return { json: JSON.parse(content) };
  } catch (e) {
    return { json: { parse_error: 'The AI did not return valid JSON', raw: content } };
  }
});

$path = "reference.html"
$text = [System.IO.File]::ReadAllText($path)
$opts = [System.Text.RegularExpressions.RegexOptions]::IgnoreCase

$patterns = @(
    '<p>Дизайн Человека 4Д<br\/>Прочтение карты по Дизайну Человека у меня стоит -\s*<br\/>Консультация -\s*<\/p>',
    '<p>Слушайте музыку с новыми смыслами нашей группы\s*<br\/>"Академия Души" в Яндексе в ВК<\/p>',
    '<p>Приглашаю в свой телеграм-канал<\/p>',
    '<p>Дизайн Человека 4Д<\/p>',
    '<p>Прочтение карты по Дизайну Человека у меня стоит -\s*<\/p>',
    '<p>Консультация -\s*<\/p>',
    'Дизайн Человека 4Д\s*\r?\nПрочтение карты по Дизайну Человека у меня стоит -\s*\r?\nКонсультация -\s*',
    'Слушайте музыку с новыми смыслами нашей группы\s*\r?\n"Академия Души" в Яндексе в ВК',
    'Приглашаю в свой телеграм-канал'
)

$total = 0
for ($i = 0; $i -lt $patterns.Count; $i++) {
    $p = $patterns[$i]
    $count = [regex]::Matches($text, $p, $opts).Count
    $total += $count
    $text = [regex]::Replace($text, $p, '', $opts)
    Write-Output ("pattern-{0}={1}" -f ($i + 1), $count)
}

$text = [regex]::Replace($text, '(\r?\n){4,}', "`r`n`r`n`r`n")
[System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding($false)))

Write-Output ("total-removed={0}" -f $total)
Write-Output ("left-4d={0}" -f ([regex]::Matches($text, '4Д').Count))
Write-Output ("left-academy={0}" -f ([regex]::Matches($text, 'Академия Души').Count))
Write-Output ("left-telegram={0}" -f ([regex]::Matches($text, 'телеграм-канал').Count))
Write-Output ("left-reading={0}" -f ([regex]::Matches($text, 'Прочтение карты').Count))

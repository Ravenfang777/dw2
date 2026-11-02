import fs from 'node:fs/promises';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root='/workspace/scratch/ac59123af99a/aqua_work';
const out='/workspace/scratch/ac59123af99a/outputs/aqua_v8';
const data=JSON.parse(await fs.readFile(`${root}/inventory_v8/Aqua_Inventory.json`,'utf8'));
await fs.mkdir(out,{recursive:true});
const wb=Workbook.create();
const clips=wb.worksheets.add('Aqua clips');
const mapping=wb.worksheets.add('KH1 assignments');
const body='#203047',head='#344966',muted='#56677E';
function setup(sheet,lastColumn,lastRow,title,note){
  sheet.showGridLines=false;
  const all=sheet.getRange(`A1:${lastColumn}${lastRow}`);
  all.format.font={name:'Arial',size:10,color:body};
  all.format.verticalAlignment='center';
  all.format.rowHeight=23;
  sheet.getRange('A2').values=[[title]];
  sheet.getRange('A2').format.font={name:'Arial',size:14,bold:true,color:body};
  sheet.getRange('A3').values=[[note]];
  sheet.getRange('A3').format.font={name:'Arial',size:10,italic:true,color:muted};
  sheet.getRange(`A4:${lastColumn}4`).format.borders={bottom:{style:'thin',color:'#B6C4D5'}};
  sheet.getRange(`A6:${lastColumn}6`).format={fill:head,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:34,wrapText:true,horizontalAlignment:'center'};
  sheet.freezePanes.freezeRows(6);sheet.freezePanes.freezeColumns(2);
  sheet.tabColor=head;
}
const rows=data.rows.map(r=>{
  const slots=data.mappings.filter(m=>m.clip_id===r.clip_id).map(m=>m.normal_slot).join(', ');
  return [r.clip_id,r.source_names,r.identification,r.confidence,r.category,r.frames,r.fps,null,r.loop_from,r.loop_to,
    r.bones,r.channels,r.keys,r.raw_flag_hex,r.interpolation_frames,
    r.primary_source.split('/').at(-1).split('::')[0],slots||'Not assigned',r.primary_source,r.animation_sha256];
});
const headers=['Clip ID','Source ID','Pose / identification','Identification status','Category','Frames','FPS','Duration (s)','Loop from','Loop to','Bones','Channels','Keyframes','PAM flags','Interpolation frames','Source bank','KH1 normal slots','Source locator','Animation SHA-256'];
setup(clips,'S',rows.length+6,'Aqua animation inventory',`${data.unique_clips} unique clips. Duration = frames / FPS. Pose labels do not establish official command names.`);
clips.getRange('A4').values=[['Loop fields are raw PAM metadata. Last sample = (frames - 1) / FPS. All copies are listed in Aqua_Source_Copies.csv.']];
clips.getRange('A4').format.font={name:'Arial',size:10,italic:true,color:muted};
clips.getRange(`B7:B${rows.length+6}`).setNumberFormat('@');
clips.getRange(`N7:N${rows.length+6}`).setNumberFormat('@');
clips.getRange(`A6:S${rows.length+6}`).values=[headers,...rows];
clips.getRange('H7').formulas=[['=F7/G7']];clips.getRange(`H7:H${rows.length+6}`).fillDown();
clips.getRange(`F7:M${rows.length+6}`).setNumberFormat('0');
clips.getRange(`H7:H${rows.length+6}`).setNumberFormat('0.000');
clips.getRange(`O7:O${rows.length+6}`).setNumberFormat('0');
const widths=[20,29,58,27,26,10,8,14,12,12,10,12,13,14,20,27,33,90,80];
for(let i=0;i<widths.length;i++)clips.getRangeByIndexes(0,i,rows.length+6,1).format.columnWidth=widths[i];
const table=clips.tables.add(`A6:S${rows.length+6}`,true,'AquaClips');table.style='TableStyleLight1';table.showFilterButton=true;
clips.getRange(`D7:D${rows.length+6}`).conditionalFormats.add('containsText',{text:'Provisional',format:{fill:'#FFF1D6',font:{color:'#73500C'}}});
clips.getRange(`D7:D${rows.length+6}`).conditionalFormats.add('containsText',{text:'Compatibility unverified',format:{fill:'#FFF1D6',font:{color:'#73500C'}}});
const mapRows=data.mappings.map(m=>[m.normal_slot,m.olympus_slot,m.request_hex,m.kh1_action,m.clip_id,m.aqua_name,m.aqua_bank,
 m.source_start_frame,m.source_end_frame,m.kh1_frames,m.kh1_fps,null,m.pose_loop?'Yes':'No',m.root_policy]);
setup(mapping,'N',mapRows.length+6,'Current KH1 animation assignments','47 normal records, 46 Olympus copies. Native KH1 events and action timing remain in use.');
mapping.getRange(`C7:C${mapRows.length+6}`).setNumberFormat('@');
mapping.getRange(`F7:F${mapRows.length+6}`).setNumberFormat('@');
mapping.getRange(`A6:N${mapRows.length+6}`).values=[['Normal slot','Olympus slot','Request','KH1 action','Aqua clip ID','Source ID','Aqua bank','Source start','Source end','KH1 frames','KH1 FPS','KH1 duration (s)','Pose loops','Root policy'],...mapRows];
mapping.getRange('L7').formulas=[['=J7/K7']];mapping.getRange(`L7:L${mapRows.length+6}`).fillDown();
mapping.getRange(`L7:L${mapRows.length+6}`).setNumberFormat('0.000');
const mapWidths=[14,17,13,33,21,13,24,15,15,15,12,20,15,22];
for(let i=0;i<mapWidths.length;i++)mapping.getRangeByIndexes(0,i,mapRows.length+6,1).format.columnWidth=mapWidths[i];
const mt=mapping.tables.add(`A6:N${mapRows.length+6}`,true,'KH1Assignments');mt.style='TableStyleLight1';mt.showFilterButton=true;
for(const [sheet,last,cols] of [[clips,rows.length+6,'S'],[mapping,mapRows.length+6,'N']]){
 sheet.getRange(`A6:${cols}6`).format={fill:head,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'}};
 for(let r=7;r<=last;r++)sheet.getRange(`A${r}:${cols}${r}`).format.fill=r%2===1?'#F1F4F8':'#FFFFFF';
}
wb.recalculate();
const sample=await wb.inspect({kind:'table',range:'Aqua clips!F6:H11',include:'values,formulas',tableMaxRows:6,tableMaxCols:3,maxChars:2200});
console.log(sample.ndjson);
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},summary:'Final formula error scan',maxChars:1800});
console.log(errors.ndjson);
for(const [name,range,file] of [['Aqua clips','A1:H15','inventory_preview.png'],['Aqua clips','I6:Q15','inventory_technical_preview.png'],['Aqua clips','R6:S12','inventory_source_preview.png'],['KH1 assignments','A1:G16','mapping_preview.png'],['KH1 assignments','H6:N16','mapping_timing_preview.png']]){
 const preview=await wb.render({sheetName:name,range,scale:1,format:'png'});
 await fs.writeFile(`${out}/${file}`,new Uint8Array(await preview.arrayBuffer()));
}
const output=await SpreadsheetFile.exportXlsx(wb);await output.save(`${out}/Aqua_Move_Inventory_v8.xlsx`);
await fs.writeFile(`${out}/spreadsheet_validation.json`,JSON.stringify({uniqueClips:rows.length,assignments:mapRows.length,formulaErrorScan:errors.ndjson,sample:sample.ndjson},null,2));
console.log(`Saved ${out}/Aqua_Move_Inventory_v8.xlsx`);

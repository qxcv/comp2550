function [coords,otherStuff] = gpsRead(DIR,name)
%[coords,otherStuff] = gpsRead(DIR,name)
%
%   DIR: source directory
%   name: which ever name to be append with 'gps'
%           examples 'h.16gps' 'h.16rgb' 'h.bmp'....
%
%   coords: gps coordinates from the gps.
%   otherStuff: Other information available at the data file.
%
%Last modification March 2010
%
%function coords = gpsRead(DIR,name)
%name is a 16raw o 16RGB
name = name(1:find(name=='.',1,'last'));
%gpsname = [name(1:end-3) 'gps'];
gpsname = [name 'gps'];
coords = [];
if exist(fullfile(DIR,gpsname),'file')==0,
    gpsname = [name '16gps'];
end
eval(['load ' '''' fullfile(DIR,gpsname) '''']);
temp  = eval([name(1:end-1)]);
%coords = eval([gpsname(1:end-6)]);
%coords = [coords1(2) coords1(1) coords1(3)];
coords = temp(1:3);
otherStuff = [];
if length(temp>3)
    otherStuff = temp(4:end);
end
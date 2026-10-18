import { boot } from './wprun.mjs';
const { php } = await boot();
const r = await php.runStream ? await php.run({ scriptPath: '/wordpress/rig-install.php' }) : await php.run({ scriptPath: '/wordpress/rig-install.php' });
console.log(r.text.slice(-400)); console.log(r.errors ? r.errors.slice(-400) : '');
process.exit(0);

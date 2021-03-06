/*
 * ------------------------------------------------------------------------
 *
 *  Copyright by KNIME AG, Zurich, Switzerland
 *  Website: http://www.knime.com; Email: contact@knime.com
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License, Version 3, as
 *  published by the Free Software Foundation.
 *
 *  This program is distributed in the hope that it will be useful, but
 *  WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, see <http://www.gnu.org/licenses>.
 *
 *  Additional permission under GNU GPL version 3 section 7:
 *
 *  KNIME interoperates with ECLIPSE solely via ECLIPSE's plug-in APIs.
 *  Hence, KNIME and ECLIPSE are both independent programs and are not
 *  derived from each other. Should, however, the interpretation of the
 *  GNU GPL Version 3 ("License") under any applicable laws result in
 *  KNIME and ECLIPSE being a combined program, KNIME AG herewith grants
 *  you the additional permission to use and propagate KNIME together with
 *  ECLIPSE with only the license terms in place for ECLIPSE applying to
 *  ECLIPSE and the GNU GPL Version 3 applying for KNIME, provided the
 *  license terms of ECLIPSE themselves allow for the respective use and
 *  propagation of ECLIPSE together with KNIME.
 *
 *  Additional permission relating to nodes for KNIME that extend the Node
 *  Extension (and in particular that are based on subclasses of NodeModel,
 *  NodeDialog, and NodeView) and that only interoperate with KNIME through
 *  standard APIs ("Nodes"):
 *  Nodes are deemed to be separate and independent programs and to not be
 *  covered works.  Notwithstanding anything to the contrary in the
 *  License, the License does not apply to Nodes, you are not required to
 *  license Nodes under the License, and you are granted a license to
 *  prepare and propagate Nodes, in each case even if such Nodes are
 *  propagated with or for interoperation with KNIME.  The owner of a Node
 *  may freely choose the license terms applicable to such Node, including
 *  when such Node is propagated with or for interoperation with KNIME.
 * ---------------------------------------------------------------------
 *
 * History
 *   Feb 26, 2019 (marcel): created
 */
package org.knime.python2.prefs;

import static org.knime.python2.prefs.PythonPreferenceUtils.performActionOnWidgetInUiThread;

import javax.swing.event.ChangeEvent;

import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StackLayout;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.events.ShellEvent;
import org.eclipse.swt.events.ShellListener;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Dialog;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.ProgressBar;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.knime.python2.config.CondaEnvironmentCreationDialog;
import org.knime.python2.config.CondaEnvironmentCreationObserver;
import org.knime.python2.config.CondaEnvironmentCreationObserver.CondaEnvironmentCreationStatus;
import org.knime.python2.config.CondaEnvironmentCreationObserver.CondaEnvironmentCreationStatusListener;

/**
 * @author Marcel Wiedenmann, KNIME GmbH, Konstanz, Germany
 * @author Christian Dietz, KNIME GmbH, Konstanz, Germany
 */
class CondaEnvironmentCreationPreferenceDialog extends Dialog implements CondaEnvironmentCreationDialog {

    private static final String CREATE_BUTTON_TEXT = "Create new environment";

    private final CondaEnvironmentCreationObserver m_environmentCreator;

    // UI components: Initialized by #createContents().

    private final Shell m_shell;

    private Label m_statusLabel;

    private StackLayout m_progressBarStackLayout;

    private ProgressBar m_indeterminateProgressBar;

    private ProgressBar m_determinateProgressBar;

    private Text m_errorTextBox;

    private Button m_cancelOrCloseButton;

    /**
     * Initialized when the create button is clicked.
     */
    private CondaEnvironmentCreationStatus m_status;

    /**
     * Initialized by {@link #registerExternalHooks()}.
     */
    private CondaEnvironmentCreationStatusListener m_statusChangeListener;

    private volatile boolean m_environmentCreationTerminated = false;

    public CondaEnvironmentCreationPreferenceDialog(final CondaEnvironmentCreationObserver environmentCreator,
        final Shell parent) {
        super(parent, SWT.NONE);
        m_environmentCreator = environmentCreator;
        m_shell = new Shell(parent, SWT.DIALOG_TRIM | SWT.SHEET);
        m_shell.setText("New Conda environment");
        createContents();
        m_shell.pack();
    }

    private void createContents() {
        m_shell.setLayout(new GridLayout());

        final Label descriptionText = new Label(m_shell, SWT.WRAP);
        descriptionText.setText("Creating the Conda environment may take several minutes"
            + "\nand requires an active internet connection.");
        descriptionText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

        // Progress monitoring widgets:

        final Composite installationMonitorContainer = new Composite(m_shell, SWT.NONE);
        installationMonitorContainer.setLayoutData(new GridData(GridData.FILL, GridData.FILL, true, true, 2, 1));
        installationMonitorContainer.setLayout(new GridLayout());

        m_statusLabel = new Label(installationMonitorContainer, SWT.WRAP);
        m_statusLabel.setText("Please click '" + CREATE_BUTTON_TEXT + "' to start.");
        GridData gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
        gridData.verticalIndent = 10;
        m_statusLabel.setLayoutData(gridData);

        final Composite progressBarContainer = new Composite(installationMonitorContainer, SWT.NONE);
        progressBarContainer.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
        m_progressBarStackLayout = new StackLayout();
        progressBarContainer.setLayout(m_progressBarStackLayout);
        m_determinateProgressBar = new ProgressBar(progressBarContainer, SWT.SMOOTH);
        m_indeterminateProgressBar = new ProgressBar(progressBarContainer, SWT.SMOOTH | SWT.INDETERMINATE);
        m_progressBarStackLayout.topControl = m_determinateProgressBar;

        final Label errorTextBoxLabel = new Label(installationMonitorContainer, SWT.NONE);
        errorTextBoxLabel.setText("Conda error log");
        gridData = new GridData();
        gridData.verticalIndent = 10;
        errorTextBoxLabel.setLayoutData(gridData);

        final Composite textBoxContainer = new Composite(installationMonitorContainer, SWT.NONE);
        gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
        gridData.heightHint = 80;
        textBoxContainer.setLayoutData(gridData);
        textBoxContainer.setLayout(new FillLayout());
        m_errorTextBox = new Text(textBoxContainer, SWT.READ_ONLY | SWT.MULTI | SWT.WRAP | SWT.V_SCROLL);
        final Color red = new Color(textBoxContainer.getDisplay(), 255, 0, 0);
        m_errorTextBox.setForeground(red);
        m_errorTextBox.addDisposeListener(e -> red.dispose());

        m_determinateProgressBar.setEnabled(false);
        m_errorTextBox.setEnabled(false);

        // --

        final Composite buttonContainer = new Composite(m_shell, SWT.NONE);
        gridData = new GridData();
        gridData.horizontalAlignment = SWT.RIGHT;
        gridData.verticalIndent = 15;
        buttonContainer.setLayoutData(gridData);
        buttonContainer.setLayout(new RowLayout());
        final Button createButton = new Button(buttonContainer, SWT.NONE);
        createButton.setText(CREATE_BUTTON_TEXT);
        m_cancelOrCloseButton = new Button(buttonContainer, SWT.NONE);
        m_cancelOrCloseButton.setText("Cancel");

        createButton.addSelectionListener(new SelectionListener() {

            @Override
            public void widgetSelected(final SelectionEvent e) {
                createButton.setEnabled(false);
                m_determinateProgressBar.setEnabled(true);
                m_errorTextBox.setEnabled(true);
                m_progressBarStackLayout.topControl = m_indeterminateProgressBar;
                m_shell.layout(true, true);
                m_status = new CondaEnvironmentCreationStatus();
                registerExternalHooks();
                m_environmentCreator.startEnvironmentCreation(m_status);
            }

            @Override
            public void widgetDefaultSelected(final SelectionEvent e) {
                widgetSelected(e);
            }
        });

        m_cancelOrCloseButton.addSelectionListener(new SelectionListener() {

            @Override
            public void widgetSelected(final SelectionEvent e) {
                if (m_status != null && !m_environmentCreationTerminated) {
                    m_environmentCreator.cancelEnvironmentCreation(m_status);
                    // Shell will be closed by the environment status listener's cancellation handler.
                } else {
                    m_shell.close();
                }
            }

            @Override
            public void widgetDefaultSelected(final SelectionEvent e) {
                widgetSelected(e);
            }
        });

        m_shell.addShellListener(new ShellListener() {

            @Override
            public void shellIconified(final ShellEvent e) {
                // no-op
            }

            @Override
            public void shellDeiconified(final ShellEvent e) {
                // no-op
            }

            @Override
            public void shellDeactivated(final ShellEvent e) {
                // no-op
            }

            @Override
            public void shellClosed(final ShellEvent e) {
                if (m_status != null && !m_environmentCreationTerminated) {
                    m_environmentCreator.cancelEnvironmentCreation(m_status);
                    // Shell will be closed by the environment status listener's cancellation/finish handlers.
                    e.doit = false;
                }
            }

            @Override
            public void shellActivated(final ShellEvent e) {
                // no-op
            }
        });
    }

    @Override
    public void open() {
        try {
            m_shell.open();
            final Display display = getParent().getDisplay();
            while (!m_shell.isDisposed()) {
                if (!display.readAndDispatch()) {
                    display.sleep();
                }
            }
        } finally {
            unregisterExternalHooks();
        }
    }

    private void registerExternalHooks() {
        m_status.getStatusMessage().addChangeListener(this::updateStatusMessage);
        m_status.getProgress().addChangeListener(this::updateProgress);
        m_status.getErrorLog().addChangeListener(this::updateErrorLog);
        m_statusChangeListener = new CondaEnvironmentCreationStatusListener() {

            @Override
            public void condaEnvironmentCreationStarting(final CondaEnvironmentCreationStatus status) {
                // no-op
            }

            @Override
            public void condaEnvironmentCreationFinished(final CondaEnvironmentCreationStatus status,
                final String createdEnvironmentName) {
                m_environmentCreationTerminated = true;
                if (status == m_status) {
                    performActionOnWidgetInUiThread(m_shell, () -> {
                        m_shell.close();
                        return null;
                    }, true);
                }
            }

            @Override
            public void condaEnvironmentCreationCanceled(final CondaEnvironmentCreationStatus status) {
                m_environmentCreationTerminated = true;
                if (status == m_status) {
                    performActionOnWidgetInUiThread(m_shell, () -> {
                        m_shell.close();
                        return null;
                    }, true);
                }
            }

            @Override
            public void condaEnvironmentCreationFailed(final CondaEnvironmentCreationStatus status,
                final String errorMessage) {
                m_environmentCreationTerminated = true;
                if (status == m_status) {
                    performActionOnWidgetInUiThread(m_shell, () -> {
                        if (!m_statusLabel.isDisposed()) {
                            final Color red = new Color(m_statusLabel.getDisplay(), 255, 0, 0);
                            m_statusLabel.setForeground(red);
                            m_statusLabel.addDisposeListener(e -> red.dispose());
                        }
                        if (!m_indeterminateProgressBar.isDisposed()) {
                            m_indeterminateProgressBar.setEnabled(false);
                        }
                        if (!m_determinateProgressBar.isDisposed()) {
                            m_determinateProgressBar.setEnabled(false);
                        }
                        if (!m_cancelOrCloseButton.isDisposed()) {
                            m_cancelOrCloseButton.setText("Close");
                        }
                        m_shell.layout(true, true);
                        return null;
                    }, true);
                }
            }
        };
        // Prepend to close dialog before installation tests on the preference page are triggered.
        m_environmentCreator.addEnvironmentCreationStatusListener(m_statusChangeListener, true);
    }

    private void unregisterExternalHooks() {
        if (m_status != null) {
            m_status.getStatusMessage().removeChangeListener(this::updateStatusMessage);
            m_status.getProgress().removeChangeListener(this::updateProgress);
            m_status.getErrorLog().removeChangeListener(this::updateErrorLog);
        }
        m_environmentCreator.removeEnvironmentCreationStatusListener(m_statusChangeListener);
    }

    private void updateStatusMessage(@SuppressWarnings("unused") final ChangeEvent e) {
        performActionOnWidgetInUiThread(m_statusLabel, () -> {
            m_statusLabel.setText(m_status.getStatusMessage().getStringValue());
            m_statusLabel.requestLayout();
            return null;
        }, true);
    }

    private void updateProgress(@SuppressWarnings("unused") final ChangeEvent e) {
        final int progress = m_status.getProgress().getIntValue();
        Control newVisibleProgressBar;
        if (progress < 100) {
            performActionOnWidgetInUiThread(m_determinateProgressBar, () -> {
                m_determinateProgressBar.setSelection(progress);
                m_determinateProgressBar.requestLayout();
                return null;
            }, true);
            newVisibleProgressBar = m_determinateProgressBar;
        } else {
            newVisibleProgressBar = m_indeterminateProgressBar;
        }
        if (m_progressBarStackLayout.topControl != newVisibleProgressBar) {
            m_progressBarStackLayout.topControl = newVisibleProgressBar;
            performActionOnWidgetInUiThread(m_shell, () -> {
                m_shell.layout(true, true);
                return null;
            }, true);
        }
    }

    private void updateErrorLog(@SuppressWarnings("unused") final ChangeEvent e) {
        performActionOnWidgetInUiThread(m_errorTextBox, () -> {
            m_errorTextBox.setText(m_status.getErrorLog().getStringValue());
            m_errorTextBox.requestLayout();
            return null;
        }, true);
    }
}

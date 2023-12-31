//
//  ShareExtensionView.swift
//  PaperPilotShareExtension
//
//  Created by 林思行 on 2023/11/14.
//

import SwiftUI
import SwiftData
import UniformTypeIdentifiers

struct ShareExtensionView: View {
    var modelContainer: ModelContainer
    var modelContext: ModelContext

    var itemProviders: [NSItemProvider]
    @State private var loading = true
    @State private var newPapers = [Paper]()
    @State private var statuses = [Result<Bool, Error>]()
    @State private var errorMsg: String?
    @State private var projects: [Project]
    @State private var selectedProjectId: Project.ID
    @State private var importing = false
    @State private var success = false

    var close: () -> Void

    init(itemProviders: [NSItemProvider], close: @escaping () -> Void) {
        self.itemProviders = itemProviders
        self.close = close
        do {
            self.modelContainer = try ModelContainer(for: Paper.self, Project.self, Bookmark.self,
                                                     User.self, MicroserviceStatus.self)
            self.modelContext = ModelContext(modelContainer)
            let projects = try modelContext.fetch(FetchDescriptor<Project>())
            self._projects = State(initialValue: projects)
            self._selectedProjectId = State(initialValue: projects.first?.id ?? Project.ID())
        } catch {
            fatalError("Could not initialize ModelContainer: \(error.localizedDescription)")
        }
    }

    var body: some View {
        NavigationStack {
            Group {
                if loading {
                    ProgressView("Loading...")
                } else if newPapers.isEmpty || errorMsg != nil {
                    VStack {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .imageScale(.large)
                            .symbolRenderingMode(.hierarchical)
                            .foregroundStyle(.red)
                            .font(.title)
                            .padding(.bottom, 4)
                        Text("Failed to import this file")
                            .foregroundStyle(.secondary)
                            .font(.title)
                        Text(errorMsg ?? String(localized: "Unsupported file type"))
                            .foregroundStyle(.secondary)
                            .font(.title3)
#if os(macOS)
                        Button("Cancel", role: .cancel, action: close)
#endif
                    }
                    .padding()
                } else {
                    Form {
#if os(macOS)
                        Section {
                            VStack {
                                Image(ImageResource.icon)
                                    .resizable()
                                    .scaledToFit()
                                    .frame(height: 64)
                                    .padding(8)
                                Text("Import Files to Paper Pilot")
                                    .font(.title2)
                            }
                            .frame(maxWidth: .infinity)
                        }
#endif
                        Section {
                            ForEach(Array(newPapers.enumerated()), id: \.offset) { index, paper in
                                LabeledContent(paper.title) {
                                    switch statuses[index] {
                                    case .success(let imported):
                                        if imported {
                                            Label("Imported", systemImage: "checkmark.circle.fill")
                                                .foregroundStyle(.green)
                                        } else {
                                            Text(paper.tempFile?.lastPathComponent ?? "")
                                        }
                                    case .failure(let error):
                                        Label(error.localizedDescription, systemImage: "exclamationmark.triangle.fill")
                                            .foregroundStyle(.red)
                                    }
                                }
                            }
                        } header: {
                            Text("Files to import")
                        } footer: {
                            Text("A paper with the same name will be created for each imported file.")
                        }

                        Section("Import to") {
                            Picker("Project", selection: $selectedProjectId) {
                                ForEach(projects) { project in
                                    Text(project.name).tag(project.id)
                                }
                            }
#if os(macOS)
                            HStack {
                                Button("Cancel", role: .cancel, action: close)
                                AsyncButton("Import \(newPapers.count) Files") {
                                    handleImport()
                                }
                                .keyboardShortcut(.defaultAction)
                            }
                            .frame(maxWidth: .infinity, alignment: .trailing)
#endif
                        }
                    }
                    .formStyle(.grouped)
                    .overlay {
                        if success {
                            VStack {
                                Image(systemName: "checkmark.circle.fill")
                                    .imageScale(.large)
                                    .symbolRenderingMode(.hierarchical)
                                    .foregroundStyle(.green)
                                    .font(.title)
                                    .padding(.bottom, 4)
                                Text("Successfully imported all files.")
                                    .foregroundStyle(.secondary)
                                    .font(.title)
                                Button("Close", action: close)
                                    .buttonStyle(.borderedProminent)
                            }
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                            .background(.regularMaterial)
                        }
                    }
                }
            }
            .navigationTitle("Import Files to Paper Pilot")
            .toolbar {
                if !success {
                    ToolbarItem(placement: .cancellationAction) {
                        Button("Cancel", role: .cancel, action: close)
                    }
                    ToolbarItem(placement: .confirmationAction) {
                        AsyncButton("Import") {
                            handleImport()
                        }
                        .disabled(newPapers.isEmpty)
                    }
                }
            }
        }
        .tint(Color("AccentColor"))
        .task {
            do {
                let identifier = UTType.fileURL.identifier
                for itemProvider in itemProviders {
                    guard itemProvider.hasItemConformingToTypeIdentifier(identifier) else { continue }
                    let item = try await itemProvider.loadItem(forTypeIdentifier: identifier)

                    var url: URL?
                    if let item = item as? URL {
                        url = item
                    } else if let urlData = item as? Data {
                        url = URL(dataRepresentation: urlData, relativeTo: nil)
                    }

                    if let url = url, url.pathExtension == "pdf" {
                        let paper = Paper(title: url.deletingPathExtension().lastPathComponent, tempFile: url)
                        newPapers.append(paper)
                        statuses.append(.success(false))
                    }
                }
            } catch {
                errorMsg = error.localizedDescription
            }
            loading = false
        }
    }

    func handleImport() {
        guard let selectedProject = projects.first(where: { $0.id == selectedProjectId }) else { return }
        guard let containerURL = FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: AppConfig.appGroupId)?
            .appending(path: "Library/Caches/ImportedFiles") else { return }
        if !FileManager.default.fileExists(atPath: containerURL.path) {
            do {
                try FileManager.default.createDirectory(at: containerURL, withIntermediateDirectories: true)
            } catch {
                errorMsg = error.localizedDescription
                return
            }
        }
        importing = true
        for (index, paper) in newPapers.enumerated() {
            if case let .success(imported) = statuses[index], imported { continue }
            do {
                guard let url = paper.tempFile else { continue }
                paper.project = selectedProject
                let didStartAccessing = url.startAccessingSecurityScopedResource()
                defer {
                    url.stopAccessingSecurityScopedResource()
                }
                if didStartAccessing {
                    let savedURL = containerURL.appending(path: "\(paper.id.uuidString).pdf")
                    try FileManager.default.copyItem(at: url, to: savedURL)
                    paper.tempFile = savedURL
                    if selectedProject.remoteId != nil {
                        paper.status = ModelStatus.waitingForUpload.rawValue
                    }
                    modelContext.insert(paper)
                    statuses[index] = .success(true)
                } else {
                    statuses[index] = .failure(PDFError.noAccess)
                    modelContext.delete(paper)
                }
            } catch {
                statuses[index] = .failure(error)
            }
        }
        importing = false
        if statuses.allSatisfy({
            if case let .success(imported) = $0 {
                return imported
            } else {
                return false
            }
        }) {
            withAnimation {
                success = true
            }
        }
    }
}
